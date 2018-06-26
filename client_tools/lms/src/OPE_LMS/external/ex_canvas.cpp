#include "ex_canvas.h"

EX_Canvas::EX_Canvas(QObject *parent, APP_DB *db, QSettings *app_settings) :
    QObject(parent)
{
    canvas_client_id = "1";
    canvas_client_secret = "hVGyxhHAKulUTZwAExbKALBpZaHTGDBkoSS7DpsvRpY1H7yzoMfnI5NLnC6t5A0Q";
    canvas_access_token = "";
    canvas_server = "https://canvas.ed";

    qmlRegisterType<EX_Canvas>("com.openprisoneducation.ope", 1, 0, "Canvas");

    // Store the app db we will use to
    if (db == NULL) {
        qDebug() << "ERROR - NO QSqlDatabase object provided in constructor!";
    }
    _app_db = db;

    if (app_settings == NULL) {
        qDebug() << "ERROR - NO QSettings object provided in constructor!";
    }
    _app_settings = app_settings;

    web_request = new CM_WebRequest(this);
    // Connect the progress signal
    connect(web_request, SIGNAL(progress(qint64,qint64)),
            this, SLOT(downloadProgress(qint64, qint64)));
}

bool EX_Canvas::pullStudentInfo()
{
    bool ret =  false;
    if (_app_db == NULL) {
       return ret;
    }

    // Get the courses table
    GenericTableModel *model = _app_db->getTable("users");
    if (model == NULL) {
        // Unable to pull the table, error with database?
        qDebug() << "ERROR pulling users table!!!";
        return false;
    }

    //qDebug() << " Trying to pull canvas student info...";

    // Pull the list of classes from the server
    QJsonDocument doc = CanvasAPICall("/api/v1/users/self");
    //qDebug() << doc.toJson();

    // Loop through the users and add them to the database
    if (doc.isObject())
    {
        // JSON Pulled:
        // {"id":26664700000000083,"name":"Smith, Bob (s777777)",
        // "sortable_name":"Smith, Bob (s777777)","short_name":"Smith, Bob (s777777)",
        // "locale":null,"permissions":{"can_update_name":true,"can_update_avatar":false}}

        QJsonObject o = doc.object();

        // Go variant first then convert to long
        QString id = o["id"].toString("");
        QString name = o["name"].toString("");
        QJsonArray permissions = o["permissions"].toArray();

        model->setFilter("id = '" + id + "'"  );
        model->select();
        QSqlRecord record;
        bool is_insert = false;
        if (model->rowCount() == 1) {
            // Row exists, update it with current info
            record = model->record(0);
            is_insert = false;
            qDebug() << "Updating student..." << name;
        } else {
            // Need to insert a record clear the filter
            model->setFilter(""); // Clear the filter
            record = model->record();
            is_insert = true;
            qDebug() << "Importing student..." << name;
        }


        record.setValue("id", o["id"].toString(""));
        record.setValue("name", o["name"].toString(""));
        record.setValue("sortable_name", o["sortable_name"].toString(""));
        record.setValue("short_name", o["short_name"].toString(""));
        record.setValue("locale", o["locale"].toString(""));
        record.setValue("permissions", QJsonDocument(o["permissions"].toObject()).toJson());

        if(is_insert) {
            model->insertRecord(-1, record);
        } else {
            // Filter should be on so record 0 should still be this record
            model->setRecord(0, record);
        }
        // Write changes to the database
        ret = model->submitAll();
        model->setFilter(""); // Clear the filter

        //qDebug() << "Student: " << name << " " << id;

        // Commit the transaction
        model->database().commit();
        //qDebug() << model->lastError();

        // Make sure to set the current user id and name in the registry
        if (_app_settings) {
            _app_settings->setValue("student/id", o["id"].toString(""));
            _app_settings->setValue("student/name", o["name"].toString(""));
            _app_settings->setValue("student/short_name", o["short_name"].toString(""));
            _app_settings->setValue("student/sortable_name", o["sortable_name"].toString(""));

        }

    }

    return ret;
}

bool EX_Canvas::pullCourses()
{
    bool ret =  false;
    QString sql = "";
    QSqlQuery query;

    if (_app_db == NULL) {
       return ret;
    }

    // Get the courses table
    GenericTableModel *model = _app_db->getTable("courses");
    if (model == NULL) {
        // Unable to pull the courses table, error with database?
        qDebug() << "ERROR pulling courses table!!!";
        return false;
    }

    //qDebug() << " Trying to pull canvas courses...";

    // Pull the list of classes from the server
    QJsonDocument doc = CanvasAPICall("/api/v1/courses");
    //qDebug() << doc.toJson();

    // Loop through the courses and add them to the database
    if (doc.isArray())
    {
        // Hide courses - re-enable them during sync
        sql = "UPDATE course SET is_active='false'";
        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
        }

        // JSON Pulled:
        // id":26664700000000082,"name":"Auto Create - CSE100","account_id":1,
        //"start_at":"2017-06-08T22:29:59Z","grading_standard_id":null,
        //"is_public":null,"course_code":"CSE100","default_view":"feed",
        //"root_account_id":1,"enrollment_term_id":1,"end_at":null,
        //"public_syllabus":false,"public_syllabus_to_auth":false,
        //"storage_quota_mb":500,"is_public_to_auth_users":false,
        //"apply_assignment_group_weights":false,
        //"calendar":{"ics":"https://canvas.ed.dev/feeds/calendars/course_1DH5m9Z2FmnmKo4pvtbTilzvUkr18C0ImOD91YNl.ics"},
        //"time_zone":"America/Denver","enrollments":[{"type":"student",
        //"role":"StudentEnrollment","role_id":3,"user_id":26664700000000083,
        //"enrollment_state":"active"}],"hide_final_grades":false,
        //"workflow_state":"available","restrict_enrollments_to_course_dates":false}

        QJsonArray arr = doc.array();
        foreach (QJsonValue val, arr)
        {
            QJsonObject o = val.toObject();
            // Go variant first then convert to long
            QString course_id = o["id"].toString("");
            QString course_name = o["name"].toString("");
            QJsonArray enrollments = o["enrollments"].toArray();
            bool isStudent = false;
            ret = true;
            foreach (QJsonValue enrollmentVal, enrollments)
            {
                QJsonObject enrollment = enrollmentVal.toObject();
                if (enrollment["type"].toString("") == "student") {
                    isStudent = true;

                    model->setFilter("id = '" + course_id + "'"  );
                    model->select();
                    QSqlRecord record;
                    bool is_insert = false;
                    if (model->rowCount() == 1) {
                        // Row exists, update it with current info
                        record = model->record(0);
                        is_insert = false;
                        qDebug() << "\tUpdating course..." << course_id << course_name;
                    } else {
                        // Need to insert a record clear the filter
                        model->setFilter(""); // Clear the filter
                        record = model->record();
                        is_insert = true;
                        qDebug() << "\tImporting course..." << course_id << course_name;
                    }


                    record.setValue("id", o["id"].toString(""));
                    record.setValue("name", o["name"].toString(""));
                    record.setValue("account_id", o["account_id"].toString(""));
                    record.setValue("start_at", o["start_at"].toString(""));
                    record.setValue("grading_standard_id", o["grading_standard_id"].toString(""));
                    record.setValue("is_public", o["is_public"].toBool(false));
                    record.setValue("course_code", o["course_code"].toString(""));
                    record.setValue("default_view", o["default_view"].toString(""));
                    record.setValue("root_account_id", o["root_account_id"].toString(""));
                    record.setValue("enrollment_term_id", o["enrollment_term_id"].toString(""));
                    record.setValue("end_at", o["end_at"].toString(""));
                    record.setValue("public_syllabus", o["public_syllabus"].toBool(false));
                    record.setValue("public_syllabus_to_auth", o["public_syllabus_to_auth"].toBool(false));
                    record.setValue("storage_quota_mb", o["storage_quota_mb"].toString(""));
                    record.setValue("is_public_to_auth_users", o["is_public_to_auth_users"].toBool(false));
                    record.setValue("apply_assignment_group_weights", o["apply_assignment_group_weights"].toBool(false));
                    record.setValue("calendar", QJsonDocument(o["calendar"].toObject()).toJson());
                    record.setValue("time_zone", o["time_zone"].toString(""));
                    record.setValue("hide_final_grades", o["hide_final_grades"].toString(""));
                    record.setValue("workflow_state", o["workflow_state"].toString(""));
                    record.setValue("restrict_enrollments_to_course_dates", o["restrict_enrollments_to_course_dates"].toBool(false));
                    record.setValue("enrollment_type", enrollment["type"].toString(""));
                    record.setValue("enrollment_role", enrollment["role"].toString(""));
                    record.setValue("enrollment_role_id", enrollment["role_id"].toString(""));
                    record.setValue("enrollment_state", enrollment["state"].toString(""));
                    record.setValue("enrollment_user_id", o["user_id"].toString(""));
                    record.setValue("is_active", "true");

                    if(is_insert) {
                        model->insertRecord(-1, record);
                    } else {
                        // Filter should be on so record 0 should still be this record
                        model->setRecord(0, record);
                    }
                    // Write changes to the database
                    if(!model->submitAll()) { ret = false; }
                    model->setFilter(""); // Clear the filter
                }
            }

            //qDebug() << "Course: " << course_name << " " << course_id << " is student " << isStudent;
        }

        // Commit the transaction
        model->database().commit();
        //qDebug() << model->lastError();
    }

    return ret;
}

bool EX_Canvas::pullModules()
{
    // Grab modules for each course in the database
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("modules");

    if (courses_model == NULL || model == NULL) {
        qDebug() << "Unable to get models for courses or modules!";
        return false;
    }

    // All enteries should be for this student, so get them all
    courses_model->setFilter("");
    ret = true;
    for (int i=0; i<courses_model->rowCount(); i++) {
        // Get modules for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        //qDebug() << "Retrieving modules for " << course_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/modules", "GET", &p);

        if (doc.isArray()) {
            qDebug() << "\tModules for course:";
            // Should be an array of modules
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a module
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");
                //qDebug() << "Module ID " << id;

                model->setFilter("id = " + id);
                model->select();
                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating module..." << id << o["name"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting module..." << id << o["name"].toString("");
                }

                // JSON - list of objects
                // {"id":26664700000000088,"name":"Module 1","position":1,"unlock_at":null,
                // "require_sequential_progress":false,"publish_final_grade":false,
                // "prerequisite_module_ids":[],"published":false,"items_count":0,
                // "items_url":"https://canvas.ed.dev/api/v1/courses/26664700000000082/modules/26664700000000088/items"}

                record.setValue("id", o["id"].toString(""));
                record.setValue("name", o["name"].toString(""));
                record.setValue("position", o["position"].toString(""));
                record.setValue("unlock_at", o["unlock_at"].toString(""));
                record.setValue("require_sequential_progress", o["require_sequential_progress"].toBool(false));
                record.setValue("publish_final_grade", o["publish_final_grade"].toBool(false));
                record.setValue("prerequisite_module_ids", QJsonDocument(o["prerequisite_module_ids"].toArray()).toJson());
                record.setValue("published", o["published"].toBool(false));
                record.setValue("items_count", o["items_count"].toString(""));
                record.setValue("items_url", o["items_url"].toString(""));
                record.setValue("course_id", course_id);

               if (is_insert) {
                   model->insertRecord(-1, record);
               } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
               }
               // Write changes
               if(!model->submitAll()) { ret = false; }
               model->setFilter(""); // clear the filter

               //qDebug() << "Module " << o["name"].toString("");
               model->database().commit();
               //qDebug() << model->lastError();

            }
        }
    }

    return ret;
}

bool EX_Canvas::pullModuleItems()
{
    // Grab module items for each module in the database
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    // Get the list of modules for this student
    GenericTableModel *modules_model = _app_db->getTable("modules");
    GenericTableModel *model = _app_db->getTable("module_items");

    if (modules_model == NULL || model == NULL) {
        qDebug() << "Unable to get models for modules or module_items!";
        return false;
    }

    // Get module items for each module
    modules_model->setFilter("");
    ret = true;
    for (int i=0; i<modules_model->rowCount(); i++) {
        // Get module_items for this module
        QSqlRecord module_record = modules_model->record(i);
        QString module_id = module_record.value("id").toString();
        QString course_id = module_record.value("course_id").toString();
        //qDebug() << "Retrieving module_items for " << module_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/modules/" + module_id + "/items", "GET", &p );

        if (doc.isArray()) {
            //qDebug() << "\t\t\tModule items for module:";
            // Should be an array of module items
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a module
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");
                //qDebug() << "Module item ID " << id;

                model->setFilter("id = " + id);
                model->select();
                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\t\tUpdating module item..." << id << o["title"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\t\tImporting module item..." << id << o["title"].toString("");
                }

                // JSON - list of objects
                // {"id":26664700000000088,"title":"Test Page","position":1,
                // "indent":0,"type":"Page","module_id":26664700000000088,
                // "html_url":"https://canvas.ed.dev/courses/26664700000000082/modules/items/26664700000000088",
                // "page_url":"test-page","url":"https://canvas.ed.dev/api/v1/courses/26664700000000082/pages/test-page",
                // "published":false}

                record.setValue("id", o["id"].toString(""));
                record.setValue("title", o["title"].toString(""));
                record.setValue("position", o["position"].toString(""));
                record.setValue("indent", o["indent"].toString(""));
                record.setValue("type", o["type"].toString(""));
                record.setValue("module_id", o["module_id"].toString(""));
                record.setValue("html_url", o["html_url"].toString(""));
                record.setValue("page_url", o["page_url"].toString(""));
                record.setValue("url", o["url"].toString(""));
                record.setValue("published", o["published"].toBool(false));
                record.setValue("content_id", o["content_id"].toString(""));
                record.setValue("external_url", o["external_url"].toString(""));
                record.setValue("new_tab", o["new_tab"].toBool(false));
                // TODO - this is an array
                record.setValue("completion_requirement", o["completion_requirement"].toString(""));
                // TOOD - also an array
                record.setValue("content_details", o["content_details"].toString(""));

               if (is_insert) {
                   model->insertRecord(-1, record);
               } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
               }
               // Write changes
               if (!model->submitAll()) { ret = false; }
               model->setFilter(""); // clear the filter

               //qDebug() << "Module item " << o["title"].toString("");
               model->database().commit();
               //qDebug() << model->lastError();

            }
        }
    }

    return ret;
}

bool EX_Canvas::pullCourseFileFolders()
{
    // Grab a list of files for each course (Non Binaries)
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("folders");

    if (courses_model == NULL || model == NULL) {
        qDebug() << "Unable to get models for courses or folders!";
        return false;
    }

    // Pull all folder info for all courses
    courses_model->setFilter("");
    ret = true;
    for (int i=0; i<courses_model->rowCount(); i++) {
        // Get folders for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        //qDebug() << "Retrieving folder info for " << course_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/folders", "GET", &p);

        if (doc.isArray()) {
            //qDebug() << "\tFolder info for course:";
            // Should be an array of folders
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a module
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");
                //qDebug() << "File ID " << id;

                model->setFilter("id = " + id);
                model->select();
                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating folder info..." << id << o["full_name"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting folder info..." << id << o["full_name"].toString("");

                }

                // JSON - list of objects
                // {"id":999999000000068,"name":"course files",
                // "full_name":"course files","context_id":999999000000068,
                // "context_type":"Course","parent_folder_id":null,
                // "created_at":"2018-02-22T21:48:37Z",
                // "updated_at":"2018-02-22T21:48:37Z","lock_at":null,
                // "unlock_at":null,"position":null,"locked":false,
                // "folders_url":"https://canvas.ed/api/v1/folders/999999000000068/folders",
                // "files_url":"https://canvas.ed/api/v1/folders/999999000000068/files",
                // "files_count":0,"folders_count":4,"hidden":null,
                // "locked_for_user":false,"hidden_for_user":false,
                // "for_submissions":false}

                record.setValue("id", o["id"].toString(""));
                record.setValue("name", o["name"].toString(""));
                record.setValue("full_name", o["full_name"].toString(""));
                record.setValue("context_id", o["context_id"].toString(""));
                record.setValue("context_type", o["context_type"].toString(""));
                record.setValue("parent_folder_id", o["parent_folder_id"].toString(""));
                record.setValue("created_at", o["created_at"].toString(""));
                record.setValue("updated_at", o["updated_at"].toString(""));
                record.setValue("lock_at", o["lock_at"].toString(""));
                record.setValue("unlock_at", o["unlock_at"].toString(""));
                record.setValue("position", o["position"].toString(""));
                record.setValue("locked", o["locked"].toBool(false));
                record.setValue("folders_url", o["folders_url"].toString(""));
                record.setValue("files_url", o["files_url"].toString(""));
                record.setValue("files_count", o["files_count"].toString("0"));
                record.setValue("folders_count", o["folders_count"].toString("0"));
                record.setValue("hidden", o["hidden"].toBool(false));
                record.setValue("locked_for_user", o["locked_for_user"].toBool(false));
                record.setValue("hidden_for_user", o["hidden_for_user"].toBool(false));
                record.setValue("for_submissions", o["for_submissions"].toBool(false));

               if (is_insert) {
                   model->insertRecord(-1, record);
               } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
               }
               // Write changes
               if (!model->submitAll()) { ret = false; }

               model->setFilter(""); // clear the filter

               //qDebug() << "File info " << o["display_name"].toString("");
               model->database().commit();
               //qDebug() << model->lastError();

            }
        }
    }

    return ret;
}

bool EX_Canvas::pullCourseFilesInfo()
{
    // Grab a list of files for each course (Non Binaries)
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("files");

    if (courses_model == NULL || model == NULL) {
        qDebug() << "Unable to get models for courses or files!";
        return false;
    }

    // Pull all file info for all courses
    courses_model->setFilter("");
    ret = true;
    for (int i=0; i<courses_model->rowCount(); i++) {
        // Get modules for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        //qDebug() << "Retrieving file info for " << course_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/files", "GET", &p);

        if (doc.isArray()) {
            //qDebug() << "\tFile info for course:";
            // Should be an array of modules
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a module
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");
                //qDebug() << "File ID " << id;

                model->setFilter("id = " + id);
                model->select();
                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating file info..." << id << o["display_name"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting file info..." << id << o["display_name"].toString("");

                    // Set some defaults
                    record.setValue("pull_file", "");
                    record.setValue("local_copy_present", "");
                }

                // JSON - list of objects
                // {"id":26664700000000097,"folder_id":26664700000000099,
                // "display_name":"101 uses of the quadratic equation.pdf",
                // "filename":"101_uses_of_the_quadratic_equation.pdf",
                // "content-type":"application/pdf",
                // "url":"https://canvas.ed.dev/files/26664700000000097/download?download_frd=1",
                // "size":451941,"created_at":"2017-06-21T21:44:11Z",
                // "updated_at":"2017-06-21T21:44:11Z","unlock_at":null,"locked":false,
                // "hidden":false,"lock_at":null,"hidden_for_user":false,
                // "thumbnail_url":null,"modified_at":"2017-06-21T21:44:11Z",
                // "mime_class":"pdf","media_entry_id":null,"locked_for_user":false}

                record.setValue("id", o["id"].toString(""));
                record.setValue("folder_id", o["folder_id"].toString(""));
                record.setValue("display_name", o["display_name"].toString(""));
                record.setValue("filename", o["filename"].toString(""));
                record.setValue("content_type", o["content-type"].toString(""));
                record.setValue("url", o["url"].toString(""));
                record.setValue("size", o["size"].toString(""));
                record.setValue("created_at", o["created_at"].toString(""));
                record.setValue("updated_at", o["updated_at"].toString(""));
                record.setValue("unlock_at", o["unlock_at"].toString(""));
                record.setValue("locked", o["locked"].toString(""));
                record.setValue("hidden", o["hidden"].toBool(false));
                record.setValue("lock_at", o["lock_at"].toString(""));
                record.setValue("hidden_for_user", o["hidden_for_user"].toBool(false));
                record.setValue("thumbnail_url", o["thumbnail_url"].toString(""));
                record.setValue("modified_at", o["modified_at"].toString(""));
                record.setValue("mime_class", o["mime_class"].toString(""));
                record.setValue("media_entry_id", o["media_entry_id"].toString(""));
                record.setValue("locked_for_user", o["locked_for_user"].toBool(false));
                record.setValue("course_id", course_id);


               if (is_insert) {
                   model->insertRecord(-1, record);
               } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
               }
               // Write changes
               if (!model->submitAll()) { ret = false; }

               model->setFilter(""); // clear the filter

               //qDebug() << "File info " << o["display_name"].toString("");
               model->database().commit();
               //qDebug() << model->lastError();

            }
        }
    }

    return ret;
}

bool EX_Canvas::pullCourseFilesBinaries()
{
    // Pull binaries for files that are marked as pull
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    GenericTableModel *files_model = _app_db->getTable("files");

    if (files_model == NULL) {
        qDebug() << "Unable to get model for files";
        return false;
    }

    files_model->setFilter(""); // pull_file=1

    // Get the local cache folder
    QDir base_dir;
    base_dir.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/file_cache/");
    base_dir.mkpath(base_dir.path());

    ret = true;
    for (int i=0; i<files_model->rowCount(); i++) {
        QSqlRecord f = files_model->record(i);
        QString f_id = f.value("id").toString();
        QString f_filename = f.value("filename").toString();
        QString f_name = f.value("display_name").toString();
        QString f_url = f.value("url").toString();
        int f_size = f.value("size").toInt();
        QString local_path = f.value("pull_file").toString();

        if (local_path == "") {
            // Assign a new local path
            local_path = "/" + f_id + "_" + f_filename;
            f.setValue("pull_file", local_path);
        }

        // See if the file already exists locally
        QFileInfo fi = QFileInfo(base_dir.path() + local_path);
        if (fi.exists() && fi.size() == f_size ) {
            qDebug() << "File exists " << f_name;
            // Mark it as present
            f.setValue("local_copy_present", true);
        } else {
            // Download the file
            qDebug() << "Downloading file " << f_name;
            progressCurrentItem = f_filename;
            bool r = DownloadFile(f_url, base_dir.path() + local_path);

            if (r == true) {
                // Mark the file as downloaded
                f.setValue("local_copy_present", true);
            }
        }

        // Write changes
        files_model->setRecord(i, f);
        files_model->submitAll();
        files_model->database().commit();
    }

    return ret;
}

bool EX_Canvas::pullCoursePages()
{
    // Grab a list of pages for each course
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("pages");

    if (courses_model == NULL || model == NULL) {
        qDebug() << "Unable to get models for courses or pages!";
        return false;
    }

    // Pull all pages for all courses
    courses_model->setFilter("");
    ret = true;
    for (int i=0; i<courses_model->rowCount(); i++) {
        // Get pages for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        qDebug() << "Retrieving page info for " << course_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/pages", "GET", &p);

        if (doc.isArray()) {
            qDebug() << "\tPages for course:";
            // Should be an array of pages
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a module
                QJsonObject o = val.toObject();

                QString id = o["page_id"].toString("");
                QString page_url = o["url"].toString("");
                QString page_body = "";

                // Need to retrieve each page body individually
                QJsonDocument page_doc = CanvasAPICall("/api/v1/courses/" + course_id + "/pages/" + page_url, "GET", &p);
                if (!page_doc.isObject()) {
                    qDebug() << "ERROR GETTING PAGE BODY - " << course_id << page_url;
                    page_body = "ERROR GETTING PAGE";
                } else {
                    QJsonObject page_object = page_doc.object();
                    page_body = page_object["body"].toString("");
                    if (page_object["locked_for_user"].toBool() == true) {
                        page_body = page_object["lock_explanation"].toString("Page Locked - see instructor");
                    }
                }

                model->setFilter("page_id = " + id);
                model->select();
                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating page..." << id << o["title"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting file info..." << id << o["title"].toString("");
                }

                // JSON - list of objects
                // {"title":"Format of the course","created_at":"2017-06-21T21:44:15Z",
                // "url":"format-of-the-course","editing_roles":"teachers",
                // "page_id":26664700000000089,"published":true,"hide_from_students":false,
                // "front_page":false,
                // "html_url":"https://canvas.ed.dev/courses/26664700000000090/pages/format-of-the-course",
                // "updated_at":"2017-06-21T21:44:15Z","locked_for_user":false}

                record.setValue("title", o["title"].toString(""));
                record.setValue("created_at", o["created_at"].toString(""));
                record.setValue("url", o["url"].toString(""));
                record.setValue("editing_roles", o["editing_roles"].toString(""));
                record.setValue("page_id", o["page_id"].toString(""));
                record.setValue("published", o["published"].toBool(false));
                record.setValue("hide_from_students", o["hide_from_students"].toBool(false));
                record.setValue("front_page", o["front_page"].toBool(false));
                record.setValue("html_url", o["html_url"].toString(""));
                record.setValue("updated_at", o["updated_at"].toString(""));
                record.setValue("locked_for_user", o["locked_for_user"].toBool(false));
                record.setValue("course_id", course_id);
                record.setValue("body", page_body);
                record.setValue("lock_info", o["lock_info"].toString(""));
                record.setValue("lock_explanation", o["lock_explanation"].toString(""));

                if (is_insert) {
                   model->insertRecord(-1, record);
                } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
                }
                // Write changes
                if (!model->submitAll()) { ret = false; }

                model->setFilter(""); // clear the filter

                //qDebug() << "Page " << o["title"].toString("");
                model->database().commit();
                //qDebug() << model->lastError();

            }
        }
    }

    return ret;
}

bool EX_Canvas::pullMessages(QString scope)
{
    // Pull the list of conversations, then pull each message in that conversation
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    if (_app_settings == NULL) {
        qDebug() << "No app settings object set!";
        return ret;
    }

    QString student_id = _app_settings->value("student/id", "").toString();
    if (student_id == "") {
        qDebug() << "No student id set!!";
        return ret;
    }

    // Get list of conversations, then pull the list of messages
    GenericTableModel *conversations_model = _app_db->getTable("conversations");
    GenericTableModel *messages_model = _app_db->getTable("messages");

    if (conversations_model == NULL || messages_model == NULL) {
        qDebug() << "Unable to get models for conversations or messages!";
        return false;
    }

    QHash<QString,QString> p;
    p["per_page"] = "10000"; // Cuts down number of calls significantly
    p["scope"] = scope;
    QJsonDocument conversations_doc = CanvasAPICall("/api/v1/conversations", "GET", &p);
    p.remove("scope"); // Remove it so we don't end up using it later
//qDebug() << "\t\tDOC " << conversations_doc;
    QSqlRecord record;
    ret = true;
    bool is_insert = false;

    // Should be an array of conversations
    if (conversations_doc.isArray()) {
        // Should have something like this:
        // [{"id":26664700000000089,"subject":"Next conversation",
        // "workflow_state":"read","last_message":"Hello",
        // "last_message_at":"2017-06-22T17:44:09Z",
        // "last_authored_message":"Is this getting through?",
        // "last_authored_message_at":"2017-06-22T05:24:11Z","message_count":2,
        // "subscribed":true,"private":false,"starred":false,"properties":[],
        // "audience":[1],
        // "audience_contexts":{"courses":{"26664700000000090":["TeacherEnrollment"]},
        // "groups":{}},"avatar_url":"https://canvas.ed.dev/images/messages/avatar-50.png",
        // "participants":[{"id":26664700000000083,"name":"Smith, Bob (s777777)"},
        // {"id":1,"name":"admin@ed"}],
        // "visible":true,"context_code":"course_26664700000000090",
        // "context_name":"TestMathCourse"},
        // {"id":26664700000000088,"subject":"Email Diag","workflow_state":"read",
        // "last_message":"It works!!!","last_message_at":"2017-06-22T05:09:16Z",
        // "last_authored_message":"Diag Email.",
        // "last_authored_message_at":"2017-06-22T04:59:37Z",
        // "message_count":2,"subscribed":true,"private":false,"starred":false,
        // "properties":[],"audience":[1],
        // "audience_contexts":{"courses":{"26664700000000090":["TeacherEnrollment"]},
        // "groups":{}},"avatar_url":"https://canvas.ed.dev/images/messages/avatar-50.png",
        // "participants":[{"id":26664700000000083,"name":"Smith, Bob (s777777)"},
        // {"id":1,"name":"admin@ed"}],"visible":true,
        // "context_code":"course_26664700000000090","context_name":"TestMathCourse"}]

        // Just pull the ID, we will pull all the details after
        // the next call since we we get all that when we pull the message list
        foreach(QJsonValue val, conversations_doc.array()) {
            // Convert this conversation to an object
            QJsonObject o = val.toObject();
            QString conversations_id = o["id"].toString("");
            if (conversations_id == "") {
                qDebug() << "ERROR ERROR - Invalid conversation? " << val.toString();
                continue;
            }

            // Make next API call to get list of messages
            QJsonDocument doc = CanvasAPICall("/api/v1/conversations/" + conversations_id, "GET", &p);
            // Should come back as an object
            if (doc.isObject()) {
                // Now pull info for the conversation and put it in the database
                o = doc.object();

                // Does this conversation exist?
                conversations_model->setFilter("id = " + conversations_id);
                conversations_model->select();
                if (conversations_model->rowCount() >= 1) {
                    // Exists
                    is_insert = false;
                    record = conversations_model->record(0);
                    qDebug() << "\tUpdating conversation " << conversations_id;
                } else {
                    // New record
                    conversations_model->setFilter("");
                    record = conversations_model->record();
                    is_insert = true;
                    qDebug() << "\tAdding conversation " << conversations_id;
                }

                // Set the values
                record.setValue("id", o["id"].toString(""));
                record.setValue("subject", o["subject"].toString(""));
                record.setValue("workflow_state", o["workflow_state"].toString(""));
                record.setValue("last_message", o["last_message"].toString(""));
                record.setValue("last_message_at", o["last_message_at"].toString(""));
                record.setValue("last_authored_message", o["last_authored_message"].toString(""));
                record.setValue("last_authored_message_at", o["last_authored_message_at"].toString(""));
                record.setValue("message_count", o["message_count"].toString(""));
                record.setValue("subscribed", o["subscribed"].toBool(false));
                record.setValue("private", o["private"].toBool(false));
                record.setValue("starred", o["starred"].toBool(false));
                record.setValue("properties", QJsonDocument(o["properties"].toArray()).toJson());
                record.setValue("audience", QJsonDocument(o["audience"].toArray()).toJson());
                record.setValue("audience_contexts", QJsonDocument(o["audience_contexts"].toObject()).toJson());
                record.setValue("avatar_url", o["avatar_url"].toString(""));
                record.setValue("participants", QJsonDocument(o["participants"].toArray()).toJson());
                record.setValue("visible", o["visible"].toBool(false));
                record.setValue("context_code", o["context_code"].toString(""));
                record.setValue("context_name", o["context_name"].toString(""));
                record.setValue("submissions", QJsonDocument(o["submissions"].toArray()).toJson());

                if (is_insert) {
                    conversations_model->insertRecord(-1, record);
                } else {
                    // Filter should be set still so 0 should be current record
                    conversations_model->setRecord(0, record);
                }
                // Write the changes
                if (!conversations_model->submitAll()) { ret = false; }

                conversations_model->setFilter(""); // clear the filter

                conversations_model->database().commit();

qDebug() << "Got conversation, going for messages: " << o["messages"];
                // Now loop through messages and put them in the database
                QJsonArray messages = o["messages"].toArray();
                foreach (QJsonValue m, messages) {
                    // Store this message in the database
                    QJsonObject mo = m.toObject();
                    QString m_id = mo["id"].toString("");
                    if (m_id == "") {
                        qDebug() << "Invalid message id! " << m.toString();
                        continue;
                    }
                    messages_model->setFilter("id = " + m_id);
                    messages_model->select();
                    if (messages_model->rowCount() >= 1) {
                        // Record exists
                        is_insert = false;
                        record = messages_model->record(0);
                        qDebug() << "\t\tUpdating message " << m_id;
                    } else {
                        // New record
                        is_insert = true;
                        messages_model->setFilter("");
                        record = messages_model->record();
                        qDebug() << "\t\tInserting new message " << m_id;
                    }

                    // Set the values
                    record.setValue("id", mo["id"].toString(""));
                    record.setValue("author_id", mo["author_id"].toString(""));
                    record.setValue("created_at", mo["created_at"].toString(""));
                    record.setValue("generated", mo["generated"].toString(""));
                    record.setValue("body", mo["body"].toString(""));
                    record.setValue("forwarded_messages", QJsonDocument(mo["forwarded_messages"].toArray()).toJson());
                    record.setValue("attachments", QJsonDocument(mo["attachments"].toArray()).toJson());
                    record.setValue("media_comment", mo["media_comment"].toString(""));
                    record.setValue("participating_user_ids", QJsonDocument(mo["participating_user_ids"].toArray()).toJson());
                    record.setValue("conversation_id", conversations_id);
                    if (mo["author_id"].toString("") == student_id) {
                        record.setValue("scope", "sent");
                    } else {
                        record.setValue("scope", "inbox");
                    }

                    if (is_insert) {
                        messages_model->insertRecord(-1, record);
                    } else {
                        // Filter should be set so 0 is current record
                        messages_model->setRecord(0, record);
                    }
                    // Write changes
                    if (!messages_model->submitAll()) { ret = false; }

                    messages_model->setFilter(""); //clear filter
                    messages_model->database().commit();
                    qDebug() << "ERR: " << messages_model->lastError();

                }

            }

            // Commit any remaining transactions
            conversations_model->database().commit();
        }
    }

    return ret;
}

bool EX_Canvas::pullAssignments()
{
    // Grab assignments for each course in the database
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    // Get a list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("assignments");

    if (courses_model == NULL || model == NULL) {
        qDebug() << "Unable to get models for courses or assignments";
        return false;
    }

    // All entries should be for this student, so get them all
    courses_model->setFilter("");
    ret = true;
    for(int i=0; i<courses_model->rowCount(); i++) {
        // Get assignments for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        QString course_name = course_record.value("name").toString();
        qDebug() << "Retrieving assignments for " << course_id;
        QHash<QString, QString> p;
        p["per_page"] = "10000"; // cut number of calls
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/assignments", "GET", &p);

        //qDebug() << "JSON Doc: " << doc;
        //qDebug() << "Is Array: " << doc.isArray();
        //qDebug() << "Is Object: " << doc.isObject();
        //qDebug() << "Is Null: " << doc.isNull();
        //qDebug() << "JSON: " << doc.toJson();

        if (doc.isArray()) {
            qDebug() << "\tAssignments for course:" << course_name;
            // Should be an array of assignments
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                // Should be an assignment
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");
                qDebug() << "Assignment ID " << id;

                model->setFilter("id = " + id);
                model->select();
                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update w current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpadting assignment..." << id << o["name"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting assignment..." << id << o["name"].toString("");
                }

                // JSON - list of objects
                // {"id": 35871700000000002,"description": null,"due_at": null,
                // "unlock_at": null,"lock_at": null,"points_possible": null,
                // "grading_type": "points","assignment_group_id": 35871700000000003,
                // "grading_standard_id": null,"created_at": "2017-09-09T23:49:06Z",
                // "updated_at": "2017-09-09T23:49:09Z","peer_reviews": false,
                // "automatic_peer_reviews": false,"position": 1,
                // "grade_group_students_individually": false,"anonymous_peer_reviews": false,
                // "group_category_id": null,"post_to_sis": false,
                // "moderated_grading": false,"omit_from_final_grade": false,
                // "intra_group_peer_reviews": false,
                // "secure_params": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsdGlfYXNzaWdubWVudF9pZCI6IjFjNTBhOTAzLWZmMWMtNDk5My1hYjg3LTY2ZWU2NWViMjY1ZiJ9.4EbPTYlKDiTZps_MxzKTlTCpXuqmzdRW7Z-q1LJX0kg",
                // "course_id": 35871700000000003,"name": "Test Assignment",
                // "submission_types": ["none"],
                // "has_submitted_submissions": false,"due_date_required": false,
                // "max_name_length": 255,"in_closed_grading_period": false,
                // "is_quiz_assignment": false,"muted": false,
                // "html_url": "https://canvas.ed/courses/35871700000000003/assignments/35871700000000002",
                // "has_overrides": false,"needs_grading_count": 0,"integration_id": null,
                // "integration_data": {},"published": true,"unpublishable": true,
                // "only_visible_to_overrides": false,"locked_for_user": false,
                // "submissions_download_url": "https://canvas.ed/courses/35871700000000003/assignments/35871700000000002/submissions?zip=1"
                //  },

                record.setValue("id", o["id"].toString(""));
                record.setValue("description", o["description"].toString(""));
                record.setValue("due_at", o["due_at"].toString(""));
                record.setValue("unlock_at", o["unlock_at"].toString(""));
                record.setValue("lock_at", o["lock_at"].toString(""));
                record.setValue("points_possible", o["points_possible"].toString(""));
                record.setValue("grading_type", o["grading_type"].toString(""));
                record.setValue("assignment_group_id", o["assignment_group_id"].toString(""));
                record.setValue("grading_standard_id", o["grading_standard_id"].toString(""));
                record.setValue("created_at", o["created_at"].toString(""));
                record.setValue("updated_at", o["updated_at"].toString(""));
                record.setValue("peer_reviews", o["peer_reviews"].toBool(false));
                record.setValue("automatic_peer_reviews", o["automatic_peer_reviews"].toBool(false));
                record.setValue("position", o["position"].toString(""));
                record.setValue("grade_group_students_individually", o["grade_group_students_individually"].toBool(false));
                record.setValue("anonymous_peer_reviews", o["anonymous_peer_reviews"].toBool(false));
                record.setValue("group_category_id", o["group_category_id"].toString(""));
                record.setValue("post_to_sis", o["post_to_sis"].toBool(false));
                record.setValue("moderated_grading", o["moderated_grading"].toBool(false));
                record.setValue("omit_from_final_grade", o["omit_from_final_grade"].toBool(false));
                record.setValue("intra_group_peer_reviews", o["intra_group_peer_reviews"].toBool(false));
                record.setValue("secure_params", o["secure_params"].toString(""));
                record.setValue("course_id", o["course_id"].toString(""));
                record.setValue("name", o["name"].toString(""));
                // Submisisons is an array, convert to comma delim string
                QJsonArray a = o["submission_types"].toArray();
                QString submission_types = "";
                foreach (QVariant v, a.toVariantList() ) {
                    if (submission_types != "") { submission_types += ","; }
                    submission_types += v.toString();
                }
                record.setValue("submission_types", submission_types);
                record.setValue("has_submitted_submissions", o["has_submitted_submissions"].toBool(false));
                record.setValue("due_date_required", o["due_date_required"].toBool(false));
                record.setValue("max_name_length", o["max_name_length"].toString(""));
                record.setValue("in_closed_grading_period", o["in_closed_grading_period"].toBool(false));
                record.setValue("is_quiz_assignment", o["is_quiz_assignment"].toBool(false));
                record.setValue("muted", o["muted"].toBool(false));
                record.setValue("html_url", o["html_url"].toString(""));
                record.setValue("has_overrides", o["has_overrides"].toBool(false));
                record.setValue("needs_grading_count", o["needs_grading_count"].toString(""));
                record.setValue("integration_id", o["integration_id"].toString(""));
                record.setValue("integration_data", o["integration_data"].toString(""));
                record.setValue("published", o["published"].toBool(false));
                record.setValue("unpublishable", o["unpublishable"].toBool(false));
                record.setValue("only_visible_to_overrides", o["only_visible_to_overrides"].toBool(false));
                record.setValue("locked_for_user", o["locked_for_user"].toBool(false));
                record.setValue("submissions_download_url", o["submissions_download_url"].toString(""));

                if (is_insert) {
                    model->insertRecord(-1, record);
                } else {
                    // Filter should be set so 0 should be current record
                    model->setRecord(0, record);
                }
                // Write changes
                if (!model->submitAll()) { ret = false; }
                model->setFilter(""); // clear the filter

                model->database().commit();

            }
        }
    }

    return ret;
}

bool EX_Canvas::pullAnnouncements()
{
    // Grab a list of announcements for each course
    bool ret = false;
    if (_app_db == NULL) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("announcements");

    if (courses_model == NULL || model == NULL) {
        qDebug() << "Unable to get models for courses or announcements!";
        return false;
    }

    // Pull all announcements for all courses
    courses_model->setFilter("");
    ret = true;
    for (int i=0; i<courses_model->rowCount(); i++) {
        // Get pages for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        qDebug() << "Retrieving page info for " << course_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        p["context_codes[]"]="course_" + course_id;
        QJsonDocument doc = CanvasAPICall("/api/v1/announcements", "GET", &p);

        if (doc.isArray()) {
            qDebug() << "\tAnnouncements for course:";
            // Should be an array of discussion topics
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // Got an item
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");

                model->setFilter("id = " + id);
                model->select();
                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating announcemnt..." << id << o["title"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting announcemnt..." << id << o["title"].toString("");
                }

                // JSON - list of objects
                /*
                 * // A discussion topic
                    {
                      // The ID of this topic.
                      "id": 1,
                      // The topic title.
                      "title": "Topic 1",
                      // The HTML content of the message body.
                      "message": "<p>content here</p>",
                      // The URL to the discussion topic in canvas.
                      "html_url": "https://<canvas>/courses/1/discussion_topics/2",
                      // The datetime the topic was posted. If it is null it hasn't been posted yet. (see
                      // delayed_post_at)
                      "posted_at": "2037-07-21T13:29:31Z",
                      // The datetime for when the last reply was in the topic.
                      "last_reply_at": "2037-07-28T19:38:31Z",
                      // If true then a user may not respond to other replies until that user has made an
                      // initial reply. Defaults to false.
                      "require_initial_post": false,
                      // Whether or not posts in this topic are visible to the user.
                      "user_can_see_posts": true,
                      // The count of entries in the topic.
                      "discussion_subentry_count": 0,
                      // The read_state of the topic for the current user, 'read' or 'unread'.
                      "read_state": "read",
                      // The count of unread entries of this topic for the current user.
                      "unread_count": 0,
                      // Whether or not the current user is subscribed to this topic.
                      "subscribed": true,
                      // (Optional) Why the user cannot subscribe to this topic. Only one reason will be
                      // returned even if multiple apply. Can be one of: 'initial_post_required': The
                      // user must post a reply first; 'not_in_group_set': The user is not in the group
                      // set for this graded group discussion; 'not_in_group': The user is not in this
                      // topic's group; 'topic_is_announcement': This topic is an announcement
                      "subscription_hold": "not_in_group_set",
                      // The unique identifier of the assignment if the topic is for grading, otherwise
                      // null.
                      "assignment_id": null,
                      // The datetime to publish the topic (if not right away).
                      "delayed_post_at": null,
                      // Whether this discussion topic is published (true) or draft state (false)
                      "published": true,
                      // The datetime to lock the topic (if ever).
                      "lock_at": null,
                      // Whether or not the discussion is 'closed for comments'.
                      "locked": false,
                      // Whether or not the discussion has been 'pinned' by an instructor
                      "pinned": false,
                      // Whether or not this is locked for the user.
                      "locked_for_user": true,
                      // (Optional) Information for the user about the lock. Present when locked_for_user
                      // is true.
                      "lock_info": null,
                      // (Optional) An explanation of why this is locked for the user. Present when
                      // locked_for_user is true.
                      "lock_explanation": "This discussion is locked until September 1 at 12:00am",
                      // The username of the topic creator.
                      "user_name": "User Name",
                      // DEPRECATED An array of topic_ids for the group discussions the user is a part
                      // of.
                      "topic_children": [5, 7, 10],
                      // An array of group discussions the user is a part of. Fields include: id,
                      // group_id
                      "group_topic_children": [{"id":5,"group_id":1}, {"id":7,"group_id":5}, {"id":10,"group_id":4}],
                      // If the topic is for grading and a group assignment this will point to the
                      // original topic in the course.
                      "root_topic_id": null,
                      // If the topic is a podcast topic this is the feed url for the current user.
                      "podcast_url": "/feeds/topics/1/enrollment_1XAcepje4u228rt4mi7Z1oFbRpn3RAkTzuXIGOPe.rss",
                      // The type of discussion. Values are 'side_comment', for discussions that only
                      // allow one level of nested comments, and 'threaded' for fully threaded
                      // discussions.
                      "discussion_type": "side_comment",
                      // The unique identifier of the group category if the topic is a group discussion,
                      // otherwise null.
                      "group_category_id": null,
                      // Array of file attachments.
                      "attachments": null,
                      // The current user's permissions on this topic.
                      "permissions": {"attach":true},
                      // Whether or not users can rate entries in this topic.
                      "allow_rating": true,
                      // Whether or not grade permissions are required to rate entries.
                      "only_graders_can_rate": true,
                      // Whether or not entries should be sorted by rating.
                      "sort_by_rating": true
                    }
                 *
                 */

                record.setValue("id", o["id"].toString(""));
                record.setValue("title", o["title"].toString(""));
                record.setValue("message", o["message"].toString(""));
                record.setValue("html_url", o["html_url"].toString(""));
                record.setValue("posted_at", o["posted_at"].toString(""));
                record.setValue("last_reply_at", o["last_reply_at"].toString(""));
                record.setValue("require_initial_post", o["require_initial_post"].toBool(false));
                record.setValue("user_can_see_posts", o["user_can_see_posts"].toBool(true));
                record.setValue("discussion_subentry_count", o["discussion_subentry_count"].toString(""));
                record.setValue("read_state", o["read_state"].toString(""));
                record.setValue("unread_count", o["unread_count"].toString(""));
                record.setValue("subscribed", o["subscribed"].toString(""));
                record.setValue("subscription_hold", o["subscription_hold"].toString(""));
                record.setValue("assignment_id", o["assignment_id"].toString(""));
                record.setValue("delayed_post_at", o["delayed_post_at"].toString(""));
                record.setValue("published", o["published"].toBool(false));
                record.setValue("lock_at", o["lock_at"].toString(""));
                record.setValue("locked", o["locked"].toBool(true));
                record.setValue("pinned", o["pinned"].toBool(false));
                record.setValue("locked_for_user", o["locked_for_user"].toBool(true));
                record.setValue("lock_info", o["lock_info"].toString(""));
                record.setValue("lock_explanation", o["lock_explanation"].toString(""));
                record.setValue("user_name", o["user_name"].toString(""));
                // this is an array [5, 7, 10]
                record.setValue("topic_children", QJsonDocument(o["topic_children"].toArray()).toJson());
                // Array of objects [{id:5, group_id:1},]
                record.setValue("group_topic_children", QJsonDocument(o["group_topic_children"].toArray()).toJson());
                record.setValue("root_topic_id", o["root_topic_id"].toString(""));
                record.setValue("podcast_url", o["podcast_url"].toString(""));
                record.setValue("discussion_type", o["discussion_type"].toString(""));
                record.setValue("group_category_id", o["group_category_id"].toString(""));
                // array
                record.setValue("attachments", QJsonDocument(o["attachments"].toArray()).toJson());
                // array
                record.setValue("permissions", QJsonDocument(o["permissions"].toArray()).toJson());
                record.setValue("allow_rating", o["allow_rating"].toBool(true));
                record.setValue("only_graders_can_rate", o["only_graders_can_rate"].toBool(true));
                record.setValue("sort_by_rating", o["sort_by_rating"].toBool(true));
                record.setValue("context_code", o["context_code"].toString(""));
                // Set this item as active
                record.setValue("active", "true");
                record.setValue("course_id", course_id);

                if (is_insert) {
                   model->insertRecord(-1, record);
                } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
                }
                // Write changes
                if (!model->submitAll()) { ret = false; }

                model->setFilter(""); // clear the filter

                //qDebug() << "Announcement " << o["title"].toString("");
                model->database().commit();
                //qDebug() << model->lastError();

            }
        } else {
            qDebug() << "Invalid Response for Announcement: " <<  doc;
        }
    }

    return ret;

}

bool EX_Canvas::pushAssignments()
{
    // Push any submitted assignments back to canvas
    bool ret = false;

    if (_app_db == NULL) { return false; }
    QSqlRecord record;
    GenericTableModel *model = NULL;

    // Get a list of assignments waiting to be submitted
    model = _app_db->getTable("assignment_submissions");
    if (!model) {
        qDebug() << "Unable to get assignment_submissions model!";
        return false;
    }

    qDebug() << "-- Pushing assignment submissions...";
    // Find submissions that have no sync date
    model->setFilter("synced_on=''");
    for (int i=0; i < model->rowCount(); i++) {
        record = model->record(i);
        qDebug() << "--- Submitting assignment file " << record.value("course_id").toString() << " " << record.value("assignment_id").toString() << " " << record.value("origin_url").toString() << "/" << record.value("queue_url").toString();
        QString course_id = record.value("course_id").toString();
        QString assignment_id = record.value("assignment_id").toString();
        QString post_file = record.value("queue_url").toString();

        QHash<QString, QString> p;
        QFileInfo fi = QFileInfo(post_file);
        p["name"] = fi.fileName();
        p["size"] = QString::number(fi.size());


        // Post to the canvas server
        // TODO
        // Get upload link
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id
                        + "/assignments/" + assignment_id
                        + "/submissions/self/files", "POST", &p);

        // Should now have the upload link
        if (doc.isObject()) {
            p.clear();
            QJsonObject o = doc.object();
            QString next_url = o["upload_url"].toString();
            QJsonObject params = o["upload_params"].toObject();
            foreach(QString key, params.keys()) {
                p[key] = params[key].toString();
            }
            QJsonDocument doc2 = CanvasAPICall(next_url, "POST", &p,
                            "multipart/form-data", post_file);
            if (doc2.isObject()) {
                // Will end up with a 201 or 301 and location header to follow
                // NetworkCall will see that and follow the link

                // Pull the file id
                QJsonObject o = doc2.object();
                QString file_id = o["id"].toString();

                // We should now have a json object with a file id, we need
                // to link it to the assignment so it shows up for the teacher
                p.clear();
                // Docs here - https://canvas.instructure.com/doc/api/submissions.html
                p["comment[text_comment]"] = "Submitted via OPE LMS App";
                p["submission[submission_type]"] = "online_upload";
                p["submission[file_ids][]"] = file_id;
//TODO - This isn't coming back with valid json document?? it gets a 201 code ?
                QJsonDocument doc3 = CanvasAPICall("/api/v1/courses/" + course_id
                        + "/assignments/" + assignment_id
                        + "/submissions", "POST", &p);
                if (doc3.isObject()) {
                    // Valid submission
                    qDebug() << "Assignment pushed - TODO";
                } else {
                    qDebug() << "Problem linking uploaded file with assignment " << doc3;
                }

            } else {
                // Invalid response??
                qDebug() << "Invalid response for upload link! " << assignment_id;
                continue; // Jump to next assignmment
            }

        } else {
            qDebug() << "Invalid json object: pushAssignments ";
        }

        // Update the database
        // TODO
        record.setValue("synced_on", QDateTime::currentDateTime().toString());
        model->setRecord(i, record);
    }
    model->submitAll();
    ret = model->database().commit();

    return ret;
}

bool EX_Canvas::pushMessages()
{
    // Push any messages back to canvas - e.g. message teacher
    bool ret = false;


    return ret;
}

bool EX_Canvas::pushFiles()
{
    // push any submitted files back to canvas - e.g. as message attachments
    bool ret = false;

    return ret;
}

bool EX_Canvas::queueAssignmentFile(QString course_id, QString assignment_id, QString submission_text, QString file_url)
{
    if (_app_db == NULL) { return false; }
    QSqlRecord record;
    GenericTableModel *model = NULL;

    // If there is a file url, try to copy it and queue it, if not, queue the text
    if (course_id == "" || assignment_id == "") { return false; }

    if (file_url != "") {
        // Convert file url (file:///) to local path
        file_url = QUrl(file_url).toLocalFile();
        submission_text = ""; // Ignore submission text if we have a file
        // See if the file exists
        if (QFile::exists(file_url)) {
            // Copy file to a temp location
            qDebug() << "Assignment file queuing up...";

            // Get the temp path for saving assignments
            QDir cache_path;
            cache_path.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/file_cache/assignment_files");
            // Make sure the base folder exists
            cache_path.mkpath(cache_path.path());

            QFileInfo fi = QFileInfo(file_url);

            QString tmp_file = QString::number(QDateTime::currentSecsSinceEpoch()) + "_" +fi.fileName();

            QString tmp_file_path = cache_path.absolutePath() + "/" + tmp_file;
            // Copy file to temp location
            QFile::copy(file_url, tmp_file_path);

            // Add the submission to the database
            model = _app_db->getTable("assignment_submissions");
            if (model == NULL) {
                qDebug() << "Unable to get model for assignment_submissions!";
                return false;
            }

            // Check if this assignment already has a submission
            // TODO - Check if assignment has already been submitted?

            // Create a new record for this assignment
            model->setFilter("");
            record = model->record();

            record.setValue("assignment_type", "file");
            record.setValue("submission_text", submission_text);
            record.setValue("queue_url", tmp_file_path);
            record.setValue("origin_url", file_url);
            record.setValue("file_size", QString::number(fi.size()));
            record.setValue("assignment_id", assignment_id);
            record.setValue("course_id", course_id);
            record.setValue("queued_on", QDateTime::currentDateTime().toString());
            record.setValue("synced_on", "");

            model->insertRecord(-1, record);

            if (!model->submitAll()) {
                qDebug() << "Error queueing assignment file in database " << model->lastError();
                model->revertAll();
                return false;
            }
            model->setFilter("");
            model->database().commit();

            return true;
        } else {
            // Invalid file submited
            qDebug() << "Submitted file doesn't exist! " << file_url;
            return false;
        }
    } else if (submission_text != "") {
        // Submitting a short answer/text response
        qDebug() << "Text answer being subbmitted";
        // TODO - Store submission text
        return true;
    } else {
        // Invalid submission?
        qDebug() << "Invalid Assignment Submission!";
        return false;
    }

    // If we get here, something isn't valid
    return false;
}


bool EX_Canvas::LinkToCanvas(QString redirect_url, QString client_id)
{
    // Redirect to canvas server to authorize this app
    bool ret = false;

    //// TODO add purpose to key generation? &purpose=MobileLMS
    // Open the browser. We will get an event from the web server when it is done
    // https://lms.dev.domain.com/login/oauth2/auth?client_id=10&response_type=code&redirect_uri=urn:ietf:wg:oauth:2.0:oob
    QString canvas_url = canvas_server;
    if (!canvas_url.endsWith("/login/oauth2/auth"))
    {
        // Add the path
        canvas_url+= "/login/oauth2/auth";
        canvas_url.replace("//login", "/login"); // fix up double slashes which happens if url already ended with /
    }
    QDesktopServices::openUrl(QUrl(canvas_url + "?client_id=" + client_id + "&response_type=code&redirect_uri=" + QUrl::toPercentEncoding(redirect_url)));
    //https://canvas.pencollege.net/login/oauth2/auth?client_id=1&response_type=code&redirect_uri=" + QUrl::toPercentEncoding("http://localhost:8080/oauth/response"))
    return true;
}

void EX_Canvas::FinalizeLinkToCanvas(CM_HTTPRequest *request, CM_HTTPResponse *response)
{


    // Get the URL and pull the parameters
    QString url = request->headers["URL"];
    QStringList parts = url.split("?");
    if (parts.length() < 2)
    {
        // Should be pre ? and post ?, so 2 parts.
        response->SetBody("<b>Invalid Query Parameters!</b>");
        return;
    }

    // Split the second item on the & to get each key=value pair
    parts = parts[1].split("&");
    QString code = "";
    // Loop till we find code
    foreach (QString part, parts)
    {
        if (part.startsWith("code"))
        {
            parts = part.split("=");
            if (parts.length() >= 2)
            {
                code = parts[1];
            }

            break;
        }
    }

    if (code == "")
    {
        // Didn't find the code param
        response->SetBody("<b>code not found!</b>");
    }

    // Now we need to post to canvas to get the final code for the user
    QHash<QString,QString> headers;
    QHash<QString,QString> params;
    params["client_id"] = canvas_client_id;
    params["client_secret"] = canvas_client_secret;
    params["code"] = code;

    QString response_string = NetworkCall(canvas_server + "/login/oauth2/token", "POST", &params, &headers);
    //qDebug() << "Token JSON: " << response_string;
    QJsonDocument d(QJsonDocument::fromJson(response_string.toUtf8()));
    if (!d.isObject())
    {
        response->SetBody("<b>Invalid canvas response!</b><br />" + response_string);
        return;
    }
    QJsonObject o = d.object();
    canvas_access_token = o["access_token"].toString();
    //qDebug() << "Access Token: " << canvas_access_token;
    if (canvas_access_token.length() > 5)
    {

    response->SetBody(tr("<b>App confirmed!</b><hr />Your app is now talking to canvas to download ") +
                      tr("your materials. You can close this browser and go back to your app if ") +
                      tr("it hasn't already done so."));

    }
    else
    {
        // Failed to get the access token?
        response->SetBody(tr("<b>Failed to authenticate with Canvas!</b><hr />We were unable to ") +
                          tr("authenticate with canvas. Please go back to your app and try again."));
    }

    //// TODO - make the app popup and save the users info and start the canvas sync

}


QJsonDocument EX_Canvas::CanvasAPICall(QString api_call, QString method, QHash<QString, QString> *p, QString content_type, QString post_file)
{
    // Network call will recursivly call the canvas api until it runs out of link headers
    QHash<QString,QString> headers;
    headers["Authorization"] = "Bearer " + canvas_access_token;
    headers["User-Agent"] = "OPE LMS";
    headers["Accept-Language"] = "en-US,en;q=0.8";

    QString call_url = api_call;
    // Don't append canvas server if full address is already present
    if (!api_call.toLower().startsWith("http")) {
        call_url = canvas_server + api_call;
    }

    QString json = NetworkCall(call_url, method, p, &headers, content_type, post_file);

    QJsonParseError *err = new QJsonParseError();
    QJsonDocument d2(QJsonDocument::fromJson(json.toUtf8(), err));
    //qDebug() << "\tJSON Parse Err: " << err->errorString() << err->offset;
    //qDebug() << "\tJSON Doc: " << d2;
    //qDebug() << "\tIs Array: " << d2.isArray();
    //qDebug() << "\tIs Object: " << d2.isObject();
    //qDebug() << "\tIs Null: " << d2.isNull();

    //http_reply_data = "{\"default_time_zone\":\"Pacific Time (US \u0026 Canada)\",\"id\":1,\"name\":\"Admin\",\"parent_account_id\":null,\"root_account_id\":null,\"default_storage_quota_mb\":5000,\"default_user_storage_quota_mb\":50}";

    // Convert big id numbers to strings so they parse correctly
    // NOTE: qjsondocument converts ints to doubles and ends up loosing presision
    // find occurences of integer values in json documents and add quotes
    QRegularExpression regex("(\"\\s*:\\s*)(\\d+\\.?\\d*)([^\"])|([\\[])(\\d+\\.?\\d*)|([,])(\\d+\\.?\\d*)"); //   ":\\s*(\\d+)\\s*,");
    json = json.replace(regex, "\\1\\4\\6\"\\2\\5\\7\"\\3");  //  :\"\\1\",");
    //qDebug() << "===================================\nParsing http data: " << json;

    // Convert response to json
    delete err;
    err = new QJsonParseError();
    QJsonDocument d(QJsonDocument::fromJson(json.toUtf8(), err));

    //qDebug() << "JSON: " << json;
    //qDebug() << "JSON Parse Err: " << err->errorString() << err->offset;
    //qDebug() << "JSON Doc: " << d;
    //qDebug() << "Is Array: " << d.isArray();
    //qDebug() << "Is Object: " << d.isObject();
    //qDebug() << "Is Null: " << d.isNull();
    //qDebug() << "JSON: " << d.toJson();

    delete err;
    return d;
}

QString EX_Canvas::NetworkCall(QString url, QString method, QHash<QString, QString> *p, QHash<QString, QString> *headers, QString content_type, QString post_file)
{
    QString ret;

    ret = web_request->NetworkCall(url, method, p, headers, content_type, post_file);
    //QByteArray bin_ret = web_request->NetworkCall(url, method, p, headers);
    //ret = QString::fromUtf8(bin_ret);

    // If this is a file push - canvas needs us to follow the 301 or 201 response
    // that should be set in the location header
    QString location_header = web_request->GetHeader("Location");
    if ((method.toUpper() == "POST" || method.toUpper() == "PUT") &&
            location_header != "") {

        // Hit the next link
        headers->clear();
        (*headers)["Authorization"] = "Bearer " + canvas_access_token;
        (*headers)["User-Agent"] = "OPE LMS";
        (*headers)["Accept-Language"] = "en-US,en;q=0.8";
        p->clear();
        return web_request->NetworkCall(location_header, "POST", p, headers);
    }

    QString link_header = web_request->GetHeader("Link");

    // For multiple pages - we follow the link header to the next page automatically
    if (link_header != "")
    {
        //qDebug() << "Link header: " << link_header;
        QString next_url = "";
        QStringList parts = link_header.split(",", QString::SkipEmptyParts);
        foreach (QString item, parts)
        {
            if(item.contains("rel=\"next\""))
            {
                // Get the link
                QStringList parts2 = item.split(";", QString::SkipEmptyParts);
                next_url = parts2[0]; // Should be the first item.
                next_url = next_url.replace("<", "").replace(">", ""); // strip off the <> tags
            }
        }

        // If there is a link header, we need to call NetworkCall recursively to get the next chunk
        if (next_url != "")
        {
            //qDebug() << "Nested API call: " << next_url;
            QString next = web_request->NetworkCall(next_url, method, p, headers, content_type, post_file);
            next = next.trimmed();
            if (next != "" && next != "[]")
            {
                // We are combining lists, so trim off the last ] of current string,
                // and the first [ of the next string

                if (ret.trimmed().endsWith("]"))
                {
                    ret = ret.remove(ret.count()-1, 1);
                }
                if (next.trimmed().startsWith("["))
                {
                    next = next.remove(0, 1);
                }
                ret.append(",");
                ret.append(next);
            }
        }
    }

    return ret;
}

bool EX_Canvas::DownloadFile(QString url, QString local_path, QString item_name)
{
    progressCurrentItem = item_name;
    return web_request->DownloadFile(url, local_path);
}

void EX_Canvas::downloadProgress(qint64 bytesRead, qint64 totalBytes)
{
    if (totalBytes == 0) {
        _dl_progress = 0;
    } else {
        _dl_progress = bytesRead / totalBytes;
    }
    emit progress(bytesRead, totalBytes, progressCurrentItem);
    emit dlProgressChanged();
}

void EX_Canvas::SetCanvasAccessToken(QString token)
{
    canvas_access_token = token;
}



/*
 *
 *
 * private static string ConvertDictionaryToQueryString(Dictionary<string, object> p)
        {
            if (p == null) { return ""; }

            StringBuilder ret = new StringBuilder();

            bool first = true;

            foreach (string key in p.Keys)
            {
                if (key == null) { continue; }

                if (p[key] == null) { p[key] = ""; }

                // Put in the & between values
                if (!first) { ret.Append("&"); }
                ret.Append(HttpUtility.UrlEncode(key));
                ret.Append("=");
                ret.Append(HttpUtility.UrlEncode(p[key].ToString()));
                first = false;
            }

            return ret.ToString();
        }

        private static Dictionary<string,object> CanvasAPICall(string api_call, string method = "GET", Dictionary<string,object> p = null)
        {
            string response_json = "";
            Dictionary<string, object> response_items;

            // Don't error out on test certs
            ServicePointManager.ServerCertificateValidationCallback = delegate { return true; };

            WebRequest wr = null;

            string qstring = "";

            if (p != null && p.Count > 0 && method.ToUpper() == "GET")
            {
                qstring = ConvertDictionaryToQueryString(p);
                wr = WebRequest.Create(canvas_server + api_call + "?" + qstring);
            }
            else
            {
                wr = WebRequest.Create(canvas_server + api_call);
            }

            wr.Headers.Add("Authorization", "Bearer " + canvas_access_token);
            //wr.Headers.Add("User-Agent", "Network Admin Tool");
            wr.Method = method.ToUpper();
            if (p != null && p.Count > 0 && (method.ToUpper() == "POST" || method.ToUpper() == "PUT"))
            {
                // Create the string boundary
                string boundary = "----------" + DateTime.Now.Ticks.ToString("x");
                wr.ContentType = "multipart/form-data;"; // boundary=" + boundary;
                //wr.ContentType = "application/x-url-formencoded";

                StringBuilder send = new StringBuilder();

                string query = ConvertDictionaryToQueryString(p);

                send.Append(query);


                // Send the whole thing off
                byte[] b = Encoding.UTF8.GetBytes(send.ToString());
                wr.ContentLength = b.Length;
                Stream st = wr.GetRequestStream();
                st.Write(b, 0, b.Length);
                st.Close();
            }

            WebResponse response = null;
            try
            {
                response = wr.GetResponse();
                Stream stream = response.GetResponseStream();
                StreamReader reader = new StreamReader(stream);
                response_json = reader.ReadToEnd();
            }
            catch { }


            // Convert JSON response to dictionary
            if (response_json.Trim() == "[]")
            {
                // Empty response, return an empty dictionary
                response_items = new Dictionary<string,object>();
            }
            else if (response_json.StartsWith("[{"))
            {
                // This is an array?
                List<Dictionary<string, object>> items = JsonConvert.DeserializeObject<List<Dictionary<string,object>>>(response_json);
                response_items = new Dictionary<string, object>();
                for (int i=0; i<items.Count; i++)
                {
                    response_items[i.ToString()] = items[i];
                }
            }
            else
            {
                response_items = JsonConvert.DeserializeObject<Dictionary<string, object>>(response_json);
            }

            if (response_items == null)
            {
                // Don't return a null, return an empty dictionary
                response_items = new Dictionary<string,object>();
            }

            return response_items;
        }


        */


