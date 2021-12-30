#include "ex_canvas.h"
#include "../appmodule.h"

EX_Canvas::EX_Canvas(QObject *parent, APP_DB *db, QSettings *app_settings, QString localhost_url) :
    QObject(parent)
{
    canvas_client_id = "1";
    canvas_client_secret = "hVGyxhHAKulUTZwAExbKALBpZaHTGDBkoSS7DpsvRpY1H7yzoMfnI5NLnC6t5A0Q";
    canvas_access_token = "";
    canvas_url = "https://canvas.ed";
    _localhost_url = localhost_url;

    qmlRegisterType<EX_Canvas>("com.openprisoneducation.ope", 1, 0, "Canvas");

    // Store the app db we will use
    if (db == nullptr) {
        qDebug() << "ERROR - NO QSqlDatabase object provided in constructor!";
    }
    _app_db = db;

    if (app_settings == nullptr) {
        qDebug() << "ERROR - NO QSettings object provided in constructor!";
    }
    _app_settings = app_settings;

    web_request = new CM_WebRequest(this);
    // Connect the progress signal
    connect(web_request, SIGNAL(progress(qint64,qint64)),
            this, SLOT(downloadProgress(qint64, qint64)));
}

bool EX_Canvas::markItemsAsInactive()
{
    bool ret = true;

    _app_db->commit();

    // Hide records - re-enable them during sync
    QString sql = "UPDATE `users` SET is_active='false'";
    QSqlQuery query;
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide courses - re-enable them during sync
    sql = "UPDATE courses SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `announcements` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `assignments` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `folders` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `files` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `pages` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `conversations` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `messages` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `module_items` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    // Hide records - re-enable them during sync
    sql = "UPDATE `modules` SET is_active='false'";
    if (!query.exec(sql)) {
        qDebug() << "DB Error: " << query.lastError().text() << query.lastQuery();
        ret = false;
    }

    _app_db->commit();

    return ret;
}

bool EX_Canvas::clearInactiveItems()
{
    bool ret = true;

    _app_db->commit();

    // Cleanup records not active
    QString cleanup_sql = "DELETE FROM `files` WHERE is_active != 'true'";
    QSqlQuery cleanup_query;
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `announcements` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `assignments` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
        ret = false;
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `folders` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
        ret = false;
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `pages` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `conversations` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
        ret = false;
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `messages` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
        ret = false;
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `module_items` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
        ret = false;
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `modules` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
        ret = false;
    }

    // Cleanup records not active
    cleanup_sql = "DELETE FROM `users` WHERE is_active != 'true'";
    if (!cleanup_query.exec(cleanup_sql)) {
        qDebug() << "DB Error: " << cleanup_query.lastError().text() << cleanup_query.lastQuery();
        ret = false;
    }

    _app_db->commit();

    return ret;
}

QString EX_Canvas::pullStudentInfo()
{
    QString ret =  "";

    if (_app_db == nullptr) {
       return "ERROR - Invalid Pointer _app_db";
    }

    // Mark items as inactive so we can tell what came in on the new sync
    markItemsAsInactive();
    reloadCourseList();

    // Get the courses table
    GenericTableModel *model = _app_db->getTable("users");
    if (model == nullptr) {
        // Unable to pull the table, error with database?
        qDebug() << "ERROR pulling users table!!!";
        return "ERROR - DB Error - getting users table";
    }

    //qDebug() << " Trying to pull canvas student info...";

    // Pull the list of classes from the server
    QHash<QString,QString> p;
    p["per_page"] = "10000"; // Cuts down number of calls significantly
    QJsonDocument doc = CanvasAPICall("/api/v1/users/self", "GET", &p);
    //qDebug() << doc.toJson();

    // Loop through the users and add them to the database
    if (doc.isObject())
    {

        // JSON Pulled:
        // {"id":26664700000000083,"name":"Smith, Bob (s777777)",
        // "sortable_name":"Smith, Bob (s777777)","short_name":"Smith, Bob (s777777)",
        // "locale":nullptr,"permissions":{"can_update_name":true,"can_update_avatar":false}}

        QJsonObject o = doc.object();

        // Go variant first then convert to long
        QString id = o["id"].toString("");
        QString name = o["name"].toString("");
        QJsonArray permissions = o["permissions"].toArray();

        if (id == "") {
            // Invalid user id?
            qDebug() << "Unable to get student information? " << doc.toJson();
            //ret = "Invalid Student ID from Canvas - stopping sync!";
            QJsonArray err_arr = o["errors"].toArray();
            QJsonObject err_obj = err_arr.first().toObject();
            ret = "ERROR - " + err_obj["message"].toString("");
            return ret;
        }

        model->setFilter("id = '" + id + "'"  );
        model->select();
        // NOTE - Make sure to fetch all or we may only get 256 records
        while(model->canFetchMore()) { model->fetchMore(); }

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
        record.setValue("is_active", "true");

        ret = o["name"].toString("");

        if(is_insert) {
            model->insertRecord(-1, record);
        } else {
            // Filter should be on so record 0 should still be this record
            model->setRecord(0, record);
        }
        // Write changes to the database
        if(!model->submitAll()) {
            qDebug() << "Error on model->submitAll()";
            ret = "ERROR - Unable to write changes to database!";
            return ret;
        }

        model->setFilter(""); // Clear the filter

        //qDebug() << "Student: " << name << " " << id;

        // Commit the transaction
        model->database().commit();
        /*  Don't check commit status? Transaction not started?
        if (!model->database().commit()) {
            qDebug() << "Error on commit!" << model->database().lastError();
            ret = "Unable to commit changes to database!";
            return ret;
        }*/
        //qDebug() << model->lastError();

        // Make sure to set the current user id and name in the registry
        if (_app_settings) {
            qDebug() << "Storing student info inthe registry...";
            _app_settings->setValue("student/id", o["id"].toString(""));
            _app_settings->setValue("student/name", o["name"].toString(""));
            _app_settings->setValue("student/short_name", o["short_name"].toString(""));
            _app_settings->setValue("student/sortable_name", o["sortable_name"].toString(""));
            _app_settings->sync();
        }

    } else {
        // Not an object? Invalid json response?
        ret = "ERROR - Invalid Json response from server: " + doc.toJson();
    }

    return ret;
}

QString EX_Canvas::autoAcceptCourses()
{
    QString ret = "";

    if (!_app_settings) {
        QString err = "ERROR - autoAcceptCourses -- No _app_settings?";
        qDebug() << err;
        return err;
    }

    QString student_id = _app_settings->value("student/id", "").toString();
    if (student_id == "") {
        // No student id? Fatal error!
        QString err = "ERROR - No student id in settings, is app credentialed?";
        qDebug() << err;
        return err;
    }

    // Get the list of courses for this user
    QHash<QString, QString> course_list;
    QHash<QString, QString> course_workflow_state;

    QString params = "?per_page=10000&state[]=unpublished&state[]=available"
            "&state[]=completed&enrollment_state[]=invited_or_pending"
            "&enrollment_state[]=active&enrollment_state[]=completed";
    QString api_url = "/api/v1/users/" + student_id + "/courses?per_page=10000&state[]=all";

    QJsonDocument doc = CanvasAPICall(api_url, "GET");
    //qDebug() << "Json Response" << doc.toJson();

    if (doc.isArray()) {
        QJsonArray arr = doc.array();
        foreach(QJsonValue val, arr) {
            QJsonObject o = val.toObject();

            QString course_id = o["id"].toString("");
            QString course_name = o["name"].toString("");
            QString course_code = o["course_code"].toString("");
            QString workflow_state = o["workflow_state"].toString("");


            if (course_name != "") {
                course_list[course_id] = course_name + " (" + course_code + ")";
                course_workflow_state[course_id] = workflow_state;
                //qDebug() << " FOUND COURSE INFO " << course_name << workflow_state;
            }
        }
    }

    // Parameters
    QHash<QString,QString> p;
    // Get the list of pending courses

    api_url = "api/v1/users/" + student_id + "/enrollments"
            "?per_page=10000&state[]=invited&state[]=creation_pending";
    doc = CanvasAPICall(api_url, "GET");

    QHash<QString, QString> course_status;

    if (doc.isArray()) {
        // Loop through entries accepting each course

        /* JSON Pulled - list of these objects
         *
         * [{"id":999999000000448,"user_id":999999000000036,"course_id":999999000000457,
         * "type":"StudentEnrollment","created_at":"2019-02-02T21:18:45Z",
         * "updated_at":"2019-02-02T21:18:45Z","associated_user_id":null,"start_at":null,
         * "end_at":null,"course_section_id":999999000000424,"root_account_id":1,
         * "limit_privileges_to_course_section":false,"enrollment_state":"creation_pending",
         * "role":"StudentEnrollment","role_id":3,"last_activity_at":null,
         * "last_attended_at":null,"total_activity_time":0,
         * "grades":{"html_url":"https://canvas.ed/courses/999999000000457/grades/999999000000036",
         * "current_grade":null,"current_score":null,"final_grade":null,"final_score":null},
         * "html_url":"https://canvas.ed/courses/999999000000457/users/999999000000036",
         * "user":{"id":999999000000036,"name":"Smith, Bob (s777777)","created_at":"2018-02-22T13:48:15-08:00","sortable_name":"Smith, Bob (s777777)","short_name":"Smith, Bob (s777777)","login_id":"s777777"}}
         *
         * */

        QJsonArray arr = doc.array();
        foreach (QJsonValue val, arr) {
            // Get the object
            QJsonObject o = val.toObject();

            QString enrollment_state = o["enrollment_state"].toString();
            QString enrollment_type = o["type"].toString();
            QString course_id = o["course_id"].toString();
            QString invitation_id = o["id"].toString();
            QString workflow_state = course_workflow_state.value(course_id);
            // Course name not returned, would need additional queries, so just use ID for now
            QString course_name = course_list.value(course_id); //QString(o["name"].toString() + " ("+ o["course_code"].toString() + ")");
            if (course_name == "") { course_name = course_id; }

            if (workflow_state == "unpublished") {
                // This course isn't published, we can't accept the enrollment yet
                qDebug() << "Course Unpublished! Students will not be able to see materials!" << course_name << course_id;
                course_status[course_id] = " - <span class='failed'>Not Accepted</span> " + course_name + " - Course not published!";
            } else if (enrollment_type != "StudentEnrollment") {
                qDebug() << "Skipping AutoAcceptCourse since enrollment isn't as a student " << course_name << enrollment_type;
                course_status[course_id] = " - <span class='failed'>Not Accepted</span> " + course_name + " - Won't accept non student enrollment (" + enrollment_type + ")";
            } else if (enrollment_state == "invited" || enrollment_state == "creation_pending") {
                // Hit the accept URL to make sure this course is accepted
                api_url = "/api/v1/courses/" + course_id + "/enrollments/" + invitation_id + "/accept";
                // DEBUG
                //api_url = "/api/v1/courses/" + course_id + "/enrollments/debug" + invitation_id + "/accept";
                p.clear();
                QString err = "Accepting enrollment for pending course " + course_id + "/" + invitation_id;
                qDebug() << err;
                //ret += err;
                QJsonDocument accept_json = CanvasAPICall(api_url, "POST", &p);
                qDebug() << "Accept Response: " << course_name << course_id << accept_json.toJson();

                // Should be an object
                if (accept_json.isObject()) {
                    QJsonObject accept_object = accept_json.object();
                    bool is_success = accept_object["success"].toBool();
                    qDebug() << "Accepted Course " << course_name << "Success: " << is_success;
                    if (is_success) {
                        course_status[course_id] = " - <span class='accepted'>Accepted</span> " + course_name;
                    } else {
                        course_status[course_id] = " - <span class='failed'>Not Accepted</span> " + course_name + " - Is course published? (" + workflow_state + ")";
                    }

                } else {
                    qDebug() << "Error activating course? " << course_name << course_id << accept_json.toJson();
                    course_status[course_id] = " - <span class='failed'>Not Accepted</span> " + course_name + " - Error accepting course, invalid Json response";
                }

            } else {
                QString err = "Skipping auto accept of pending course " + course_id + " - " + invitation_id + " - " + enrollment_type + " - " + enrollment_state + " - " + student_id;
                qDebug() << err;
                //ret += err;
                course_status[course_id] = " - <span class='failed'>No Accepted</span> " + course_name + " - Skipping due to unknown state (" + enrollment_state + ")";
            }
        }

    } else {
        QString err = "ERROR - Invalid JSON Response in autoAcceptCourses\n  " + doc.toJson();
        qDebug() << err;
        ret = err;
    }


    // Build up output to return
    if (course_status.count() > 0) {
        // Loop through each course listed and add output
        foreach (QString key, course_status.keys()) {
            QString course_name = key;
            // Translate from course id to course name
            if (course_list.contains(key)) {
                course_name = course_list[key];
            }
            ret += course_status[key] + "\n";
        }
    } else {
        // No courses found to accept
        ret += " - No invitations found";
    }

    return ret;
}

QString EX_Canvas::pullCourses()
{
    QString ret =  "";
    QString sql = "";
    QSqlQuery query;

    if (_app_db == nullptr) {
       return "ERROR - No valid _app_db";
    }

    // Get the courses table
    GenericTableModel *model = _app_db->getTable("courses");
    if (model == nullptr) {
        // Unable to pull the courses table, error with database?
        QString err = "ERROR - pulling courses table!!!";
        qDebug() << err;
        return err;
    }

    //qDebug() << " Trying to pull canvas courses...";

    // Pull the list of classes from the server
    QHash<QString,QString> p;
    //p["per_page"] = "10000"; // Cuts down number of calls significantly
    // Add extra filter so we get ALL courses (even unpublished and pending)
    //p["state[]"] = "all";
    QJsonDocument doc = CanvasAPICall("/api/v1/courses?per_page=10000&state[]=all", "GET", &p);
    //qDebug() << doc.toJson();

    QHash<QString, QString> courses_pulled;


    // Loop through the courses and add them to the database
    if (doc.isArray())
    {

        // JSON Pulled:
        // id":26664700000000082,"name":"Auto Create - CSE100","account_id":1,
        //"start_at":"2017-06-08T22:29:59Z","grading_standard_id":nullptr,
        //"is_public":nullptr,"course_code":"CSE100","default_view":"feed",
        //"root_account_id":1,"enrollment_term_id":1,"end_at":nullptr,
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
            bool access_restricted_by_date = o["access_restricted_by_date"].toBool();
            QString course_name = o["name"].toString("");
            QJsonArray enrollments = o["enrollments"].toArray();
            bool isStudent = false;
            bool isTA_plus = false; // marked for any other enrollment besides student
            bool is_active = true; // determine if course/enrollment is active
            QString enrollment_type = "";
            QString enrollment_role = "";
            QString enrollment_role_id = "";
            QString enrollment_state = "";
            QString workflow_state = o["workflow_state"].toString("");
            //  ---- this helps prevent TAs from uploading things and syncing those classes
            bool is_syncing = false; // Are we going to sync this course?


            foreach (QJsonValue enrollmentVal, enrollments)
            {
                QJsonObject enrollment = enrollmentVal.toObject();
                if (enrollment["type"].toString("") == "student" &&
                        (enrollment["enrollment_state"] == "active" ||
                         enrollment["enrollment_state"] == "invited")) {

                    isStudent = true;

                    enrollment_type = enrollment["type"].toString("");
                    enrollment_role = enrollment["role"].toString("");
                    enrollment_role_id = enrollment["role_id"].toString("");
                    enrollment_state = enrollment["enrollment_state"].toString("");

                    qDebug() << "   --> Found active student enrollment " << course_name << ":" << course_id << ":" << enrollment["type"];
                } else if (enrollment["type"].toString("") == "student" &&
                        enrollment["enrollment_state"] != "active") {
                    // Student but not active
                    enrollment_state = enrollment["enrollment_state"].toString("");
                    qDebug() << "   --> Found inactive student enrollment (not syncing) " << course_name << ":" << course_id << ":" << enrollment["type"];
                    is_active = false;
                    isStudent = true;
                } else {
                    qDebug() << "   --> Found NON student enrollment (not syncing) " << course_name << ":" << course_id << ":" << enrollment["type"];
                    enrollment_state = enrollment["enrollment_state"].toString("");
                    isTA_plus = true;
                }
            }

            qDebug() << "ACCESS: " << access_restricted_by_date;

            if (access_restricted_by_date == true) {
                courses_pulled[course_id] = " - <span class='failed'>NOT SYNCING</span> " + course_id + " - COURSE RESTRICTED BY DATE";
                qDebug() << "*** Course access restricted by date - not syncing " << course_name << ":" << course_id;
            } else if (workflow_state != "available") {
                courses_pulled[course_name] = " - <span class='failed'>NOT SYNCING</span> " + course_name + " - Course not published? (" + workflow_state + "/" + enrollment_state + ")";
                qDebug() << "*** Course not published - not syncing " << course_name << ":" << course_id;
            }else if (isStudent == true && is_active == true && isTA_plus != true) {
                is_syncing = true;
                // Is a student, but NOT a TA or higher... do the sync.
                model->setFilter("id = '" + course_id + "'"  );
                model->select();
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

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
                record.setValue("enrollment_type", enrollment_type);
                record.setValue("enrollment_role", enrollment_role);
                record.setValue("enrollment_role_id", enrollment_role_id);
                record.setValue("enrollment_state", enrollment_state);
                record.setValue("enrollment_user_id", o["user_id"].toString(""));
                record.setValue("is_active", "true");

                if(is_insert) {
                    model->insertRecord(-1, record);
                } else {
                    // Filter should be on so record 0 should still be this record
                    model->setRecord(0, record);
                }
                // Write changes to the database
                if(!model->submitAll()) {
                    qDebug() << "Error submitting database changes " << model->database().lastError();
                    return "ERROR - Unable to submit database changes!";
                }
                model->setFilter(""); // Clear the filter

                if (is_syncing) {
                    courses_pulled[course_name] = " - <span class='accepted'>SYNCING</span> " + course_name + " (" + workflow_state + "/" + enrollment_state + ")";
                } else {
                    courses_pulled[course_name] = " - <span class='failed'>NOT SYNCING</span> " + course_name + " (" + workflow_state + "/" + enrollment_state + ")";
                }

            }else if (isStudent == true && is_active != true) {
                // Log that we aren't syncing this course
                courses_pulled[course_name] = " - <span class='failed'>NOT SYNCING</span> " + course_name + " - Enrollment isn't active (" + workflow_state + "/" + enrollment_state + ")";
                qDebug() << "*** Course enrollment isn't active, not syncing this course " << course_name << ":" << course_id;
            } else {
                // Log that we aren't syncing this course
                courses_pulled[course_name] = " - <span class='failed'>NOT SYNCING</span> " + course_name + " - TA+ permissions found, will only sync student access (" + workflow_state + "/" + enrollment_state + ")";
                qDebug() << "*** TA+ permissions detected, not syncing this course " << course_name << ":" << course_id;
            }
            //qDebug() << "Course: " << course_name << " " << course_id << " is student " << isStudent;
        }

        // Commit the transaction
        model->database().commit();
        //qDebug() << model->lastError();
    }

    // Remove any courses that are not active=true
    QSqlQuery q;
    q.prepare("DELETE FROM courses WHERE is_active != 'true'");
    if (!q.exec()) {
        qDebug() << "ERROR - SQL Query Failed: " << q.lastError();
    } else {
        _app_db->commit();
    }

    // Clear the dl_queue
    q.clear();
    q.prepare("DELETE FROM canvas_dl_queue");
    if (!q.exec()) {
        qDebug() << "ERROR - SQL Query Failed: " << q.lastError();
    } else {
        _app_db->commit();
    }

    // Clear the SMC media dl queue
    q.clear();
    q.prepare("DELETE FROM smc_media_dl_queue2");
    if (!q.exec()) {
        qDebug() << "ERROR - SQL Query Failed: " << q.lastError();
    } else {
        _app_db->commit();
    }

    // Clear the SMC document dl queue
    q.clear();
    q.prepare("DELETE FROM smc_document_dl_queue2");
    if (!q.exec()) {
        qDebug() << "ERROR - SQL Query Failed: " << q.lastError();
    } else {
        _app_db->commit();
    }

    // Make sure the list of courses in memory is reloaded for later use
    reloadCourseList();

    // Return the list of courses
    foreach (QString key, courses_pulled.keys()) {
        ret += courses_pulled[key] + "\n";
    }

    return ret;
}

QString EX_Canvas::pullDiscussionTopics()
{
    // Grab discussion topics for each course in the database
    QString ret = "";
    if (_app_db == nullptr) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("discussion_topics");

    if (courses_model == nullptr || model == nullptr) {
        QString err = "ERROR - Unable to get models for courses or discussion topics!";
        qDebug() << err;
        return err;
    }

    // All enteries should be for this student, so get them all
    courses_model->setFilter("");
    courses_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(courses_model->canFetchMore()) { courses_model->fetchMore(); }

    ret = true;
    int rowCount = courses_model->rowCount();
    for (int i=0; i<rowCount; i++) {
        // Get modules for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        //qDebug() << "Retrieving modules for " << course_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/discussion_topics", "GET", &p);

        if (doc.isArray()) {
            qDebug() << "\tDiscussion Topics for course:";

            // Should be an array of discussion topics
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a topic
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");
                //qDebug() << "Discussion Topic ID " << id;

                model->setFilter("id = " + id);
                model->select();
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating discussion topic..." << id << o["title"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting discussion topic..." << id << o["title"].toString("");
                }

                // JSON - list of objects
                /*
// A discussion topic
{
  // The ID of this topic.
  "id": 1,
  // The topic title.
  "title": "Topic 1",
  // The HTML content of the message body.
  "message": "<p>content here</p>",
  // The URL to the discussion topic in canvas.
  "html_url": "https://<canvas>/courses/1/discussion_topics/2",
  // The datetime the topic was posted. If it is null it hasn't been posted yet.
  // (see delayed_post_at)
  "posted_at": "2037-07-21T13:29:31Z",
  // The datetime for when the last reply was in the topic.
  "last_reply_at": "2037-07-28T19:38:31Z",
  // If true then a user may not respond to other replies until that user has made
  // an initial reply. Defaults to false.
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
  // (Optional) Why the user cannot subscribe to this topic. Only one reason will
  // be returned even if multiple apply. Can be one of: 'initial_post_required':
  // The user must post a reply first; 'not_in_group_set': The user is not in the
  // group set for this graded group discussion; 'not_in_group': The user is not
  // in this topic's group; 'topic_is_announcement': This topic is an announcement
  "subscription_hold": "not_in_group_set",
  // The unique identifier of the assignment if the topic is for grading,
  // otherwise null.
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
  // (Optional) Information for the user about the lock. Present when
  // locked_for_user is true.
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
  // The unique identifier of the group category if the topic is a group
  // discussion, otherwise null.
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

                 */

                record.setValue("id", o["id"].toString(""));
                record.setValue("course_id", course_id);
                record.setValue("title", o["title"].toString(""));
                record.setValue("message", o["message"].toString(""));
                record.setValue("html_url", o["html_url"].toString(""));
                record.setValue("posted_at", o["posted_at"].toString(""));
                record.setValue("last_reply_at", o["last_reply_at"].toString(""));
                record.setValue("require_initial_post", o["require_initial_post"].toString(""));
                record.setValue("user_can_see_posts", o["user_can_see_posts"].toBool(true));
                record.setValue("discussion_subentry_count", o["discussion_subentry_county"].toString("0"));
                record.setValue("read_state", o["read_state"].toString("unread"));
                record.setValue("unread_count", o["unread_count"].toString(""));
                record.setValue("subscribed", o["subscribed"].toBool(true));
                record.setValue("subscription_hold", o["subscription_hold"].toString("not_in_group_set"));
                record.setValue("assignment_id", o["assignment_id"].toString(""));
                record.setValue("delayed_post_at", o["delayed_post_at"].toString(""));
                record.setValue("published", o["published"].toBool(true));
                record.setValue("lock_at", o["lock_at"].toString(""));
                record.setValue("locked", o["locked"].toBool(false));
                record.setValue("pinned", o["pinned"].toBool(false));
                record.setValue("locked_for_user", o["locked_for_user"].toBool(false));
                record.setValue("lock_info", o["lock_info"].toString(""));
                record.setValue("lock_explanation", o["lock_explanation"].toString(""));
                record.setValue("user_name", o["user_name"].toString(""));
                record.setValue("topic_children", QJsonDocument(o["topic_children"].toObject()).toJson());
                record.setValue("group_topic_children", QJsonDocument(o["group_topic_children"].toObject()).toJson());
                record.setValue("root_topic_id", o["root_topic_id"].toString(""));
                record.setValue("podcast_url", o["podcast_url"].toString(""));
                record.setValue("discussion_type", o["discussion_type"].toString("side_comment"));
                record.setValue("group_category_id", o["group_category_id"].toString(""));
                record.setValue("attachments", o["attachments"].toString(""));
                record.setValue("permissions", QJsonDocument(o["permissions"].toObject()).toJson());
                record.setValue("allow_rating", o["allow_rating"].toBool(true));
                record.setValue("only_graders_can_rate", o["only_graders_can_rate"].toBool(true));
                record.setValue("sort_by_rating", o["sort_by_rating"].toBool(true));
                record.setValue("is_active", "true");

                if (is_insert) {
                   model->insertRecord(-1, record);
                } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
                }
                // Write changes
                if(!model->submitAll()) {
                    ret = "Error saving discussion topic! ";
                    qDebug() << "ERROR - problem saving discussion topic " << id << model->lastError();
                }
                model->setFilter(""); // clear the filter

                //qDebug() << "Module " << o["name"].toString("");
                model->database().commit();
                //qDebug() << model->lastError();

            }
        }
    }

    return ret;
}

QString EX_Canvas::pullQuizzes()
{
    // Grab discussion topics for each course in the database
    QString ret = "";
    if (_app_db == nullptr) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("quizzes");

    if (courses_model == nullptr || model == nullptr) {
        QString err = "ERROR - Unable to get models for courses or quizzes!";
        qDebug() << err;
        return err;
    }

    // All enteries should be for this student, so get them all
    courses_model->setFilter("");
    courses_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(courses_model->canFetchMore()) { courses_model->fetchMore(); }

    ret = true;
    int rowCount = courses_model->rowCount();
    for (int i=0; i<rowCount; i++) {
        // Get quizzes for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        //qDebug() << "Retrieving quizzes for " << course_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/quizzes", "GET", &p);

        if (doc.isArray()) {
            qDebug() << "\tQuizzes for course: " << course_id;

            // Should be an array of discussion topics
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a quiz
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");
                //qDebug() << "Quiz ID " << id;

                model->setFilter("id = " + id);
                model->select();
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating quiz..." << id << o["title"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting quiz..." << id << o["title"].toString("");
                }
                ret += "\n\tProcessing Quiz: " + QString(id) + " - " + o["title"].toString("");

                // JSON - list of objects
                /*
// A quiz
{
  // the ID of the quiz
  "id": 5,
  // the title of the quiz
  "title": "Hamlet Act 3 Quiz",
  // the HTTP/HTTPS URL to the quiz
  "html_url": "http://canvas.example.edu/courses/1/quizzes/2",
  // a url suitable for loading the quiz in a mobile webview.  it will persiste
  // the headless session and, for quizzes in public courses, will force the user
  // to login
  "mobile_url": "http://canvas.example.edu/courses/1/quizzes/2?persist_healdess=1&force_user=1",
  // A url that can be visited in the browser with a POST request to preview a
  // quiz as the teacher. Only present when the user may grade
  "preview_url": "http://canvas.example.edu/courses/1/quizzes/2/take?preview=1",
  // the description of the quiz
  "description": "This is a quiz on Act 3 of Hamlet",
  // type of quiz possible values: 'practice_quiz', 'assignment', 'graded_survey',
  // 'survey'
  "quiz_type": "assignment",
  // the ID of the quiz's assignment group:
  "assignment_group_id": 3,
  // quiz time limit in minutes
  "time_limit": 5,
  // shuffle answers for students?
  "shuffle_answers": false,
  // let students see their quiz responses? possible values: null, 'always',
  // 'until_after_last_attempt'
  "hide_results": "always",
  // show which answers were correct when results are shown? only valid if
  // hide_results=null
  "show_correct_answers": true,
  // restrict the show_correct_answers option above to apply only to the last
  // submitted attempt of a quiz that allows multiple attempts. only valid if
  // show_correct_answers=true and allowed_attempts > 1
  "show_correct_answers_last_attempt": true,
  // when should the correct answers be visible by students? only valid if
  // show_correct_answers=true
  "show_correct_answers_at": "2013-01-23T23:59:00-07:00",
  // prevent the students from seeing correct answers after the specified date has
  // passed. only valid if show_correct_answers=true
  "hide_correct_answers_at": "2013-01-23T23:59:00-07:00",
  // prevent the students from seeing their results more than once (right after
  // they submit the quiz)
  "one_time_results": true,
  // which quiz score to keep (only if allowed_attempts != 1) possible values:
  // 'keep_highest', 'keep_latest'
  "scoring_policy": "keep_highest",
  // how many times a student can take the quiz -1 = unlimited attempts
  "allowed_attempts": 3,
  // show one question at a time?
  "one_question_at_a_time": false,
  // the number of questions in the quiz
  "question_count": 12,
  // The total point value given to the quiz
  "points_possible": 20,
  // lock questions after answering? only valid if one_question_at_a_time=true
  "cant_go_back": false,
  // access code to restrict quiz access
  "access_code": "2beornot2be",
  // IP address or range that quiz access is limited to
  "ip_filter": "123.123.123.123",
  // when the quiz is due
  "due_at": "2013-01-23T23:59:00-07:00",
  // when to lock the quiz
  "lock_at": null,
  // when to unlock the quiz
  "unlock_at": "2013-01-21T23:59:00-07:00",
  // whether the quiz has a published or unpublished draft state.
  "published": true,
  // Whether the assignment's 'published' state can be changed to false. Will be
  // false if there are student submissions for the quiz.
  "unpublishable": true,
  // Whether or not this is locked for the user.
  "locked_for_user": false,
  // (Optional) Information for the user about the lock. Present when
  // locked_for_user is true.
  "lock_info": null,
  // (Optional) An explanation of why this is locked for the user. Present when
  // locked_for_user is true.
  "lock_explanation": "This quiz is locked until September 1 at 12:00am",
  // Link to Speed Grader for this quiz. Will not be present if quiz is
  // unpublished
  "speedgrader_url": "http://canvas.instructure.com/courses/1/speed_grader?assignment_id=1",
  // Link to endpoint to send extensions for this quiz.
  "quiz_extensions_url": "http://canvas.instructure.com/courses/1/quizzes/2/quiz_extensions",
  // Permissions the user has for the quiz
  "permissions": null,
  // list of due dates for the quiz
  "all_dates": null,
  // Current version number of the quiz
  "version_number": 3,
  // List of question types in the quiz
  "question_types": ["multiple_choice", "essay"],
  // Whether survey submissions will be kept anonymous (only applicable to
  // 'graded_survey', 'survey' quiz types)
  "anonymous_submissions": false
}

                 */

                record.setValue("id", o["id"].toString(""));
                record.setValue("course_id", course_id);
                record.setValue("title", o["title"].toString(""));
                record.setValue("html_url", o["html_url"].toString(""));
                record.setValue("mobile_url", o["mobile_url"].toString(""));
                record.setValue("preview_url", o["preview_url"].toString(""));
                record.setValue("description", o["description"].toString(""));
                record.setValue("quiz_type", o["quiz_type"].toString(""));
                record.setValue("assignment_group_id", o["assignment_group_id"].toString(""));
                record.setValue("time_limit", o["time_limit"].toString(""));
                record.setValue("shuffle_answers", o["shuffle_answers"].toBool(false));
                record.setValue("hide_results", o["hide_results"].toString("")); // always, null, until_after_last_attempt
                record.setValue("show_correct_answers", o["show_correct_answers"].toBool(true));
                record.setValue("show_correct_answers_last_attempt", o["show_correct_answers_last_attempt"].toBool(true));
                record.setValue("show_correct_answers_at", o["show_correct_answers_at"].toString(""));
                record.setValue("hide_correct_answers_at", o["hide_correct_answers_at"].toString(""));
                record.setValue("one_time_results", o["one_time_results"].toBool(true));
                record.setValue("scoring_policy", o["scoring_policy"].toString(""));
                record.setValue("allowed_attempts", o["allowed_attempts"].toString(""));
                record.setValue("one_question_at_a_time", o["one_question_at_a_time"].toBool(false));
                record.setValue("question_count", o["question_count"].toString(""));
                record.setValue("points_possible", o["points_possible"].toString(""));
                record.setValue("cant_go_back", o["cant_go_back"].toBool(false));
                record.setValue("has_access_code", o["has_access_code"].toBool(false));

                // NOTE - access code not coming down?
                QString access_code = o["access_code"].toString("");
                if (access_code != "") {
                    // Hash the code so students can't see it
                    QCryptographicHash hash(QCryptographicHash::Sha256);
                    hash.addData(access_code.toLocal8Bit());
                    access_code = hash.result().toHex();
                }
                record.setValue("access_code", access_code); // Need to hash?
                record.setValue("ip_filter", o["ip_filter"].toString(""));
                record.setValue("due_at", o["due_at"].toString(""));
                record.setValue("lock_at", o["lock_at"].toString(""));
                record.setValue("unlock_at", o["unlock_at"].toString(""));
                record.setValue("published", o["published"].toBool(true));
                record.setValue("unpublishable", o["unpublishable"].toBool(true));
                record.setValue("locked_for_user", o["locked_for_user"].toBool(false));
                record.setValue("lock_info", o["lock_info"].toString(""));
                record.setValue("lock_explanation", o["lock_explanation"].toString(""));
                record.setValue("speedgrader_url", o["speedgrader_url"].toString(""));
                record.setValue("quiz_extensions_url", o["quiz_extensions_url"].toString(""));
                record.setValue("permissions", QJsonDocument(o["permissions"].toObject()).toJson());
                record.setValue("all_dates", QJsonDocument(o["all_dates"].toObject()).toJson());
                record.setValue("version_number", o["version_number"].toString(""));
                record.setValue("question_types", QJsonDocument(o["question_types"].toObject()).toJson());
                record.setValue("anonymous_submissions", o["anonymous_submissions"].toBool(false));
                record.setValue("is_active", "true");

                if (is_insert) {
                   model->insertRecord(-1, record);
                } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
                }
                // Write changes
                if(!model->submitAll()) {
                    ret += "\n\t\tError saving quiz! " + QString(id) + " - " + o["title"].toString("");
                    qDebug() << "ERROR - problem saving quiz " << id << model->lastError();
                }
                model->setFilter(""); // clear the filter

                //qDebug() << "Quiz " << o["name"].toString("");
                model->database().commit();
                //qDebug() << model->lastError();

            }
        }
    }
    ret += "\nDone pulling quizzes";

    return ret;
}


QString EX_Canvas::pullQuizQuestions()
{
    // NOTE - This has to bounce through SMC since canvas doesn't give up
    // quizzes and answers through the API

    // Grab questions for each course in the database
    QString ret = "";
    if (_app_db == nullptr) { return ret; }

    // Get the list of quizzes for this student
    GenericTableModel *quizzes_model = _app_db->getTable("quizzes");
    GenericTableModel *model = _app_db->getTable("quiz_questions");

    if (quizzes_model == nullptr || model == nullptr) {
        QString err = "ERROR - Unable to get models for quizzes or quiz_questions!";
        qDebug() << err;
        return err;
    }

    // All enteries should be for this student, so get them all
    quizzes_model->setFilter("");
    quizzes_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(quizzes_model->canFetchMore()) { quizzes_model->fetchMore(); }

    // Get the student username/userid
    QString student_user = _app_settings->value("student/user_name", "").toString();
    QString smc_url = _app_settings->value("student/smc_url", "https://smc.ed").toString();
    if (!smc_url.endsWith("/")){ smc_url += "/"; }

    ret = true;
    int rowCount = quizzes_model->rowCount();
    for (int i=0; i<rowCount; i++) {
        // Get quiz questions for this quiz
        QSqlRecord quiz_record = quizzes_model->record(i);
        QString quiz_id = quiz_record.value("id").toString();
        QString course_id = quiz_record.value("course_id").toString();
        //qDebug() << "Retrieving quiz questions for " << quiz_id;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        //QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/quizzes/" + quiz_id + "/questions", "GET", &p);

        //QJsonDocument doc = SMCAPICall("/lms/get_quiz_questions/" + student_user + "/" + course_id + "/" + quiz_id + "/<auth_key>", "GET", &p);
        QString api_url = smc_url + "lms/get_quiz_questions_for_student/" + student_user + "/" + course_id + "/" + quiz_id + "/" + canvas_access_token;
        QHash<QString,QString> headers;
        headers["Authorization"] = "Bearer " + canvas_access_token;
        headers["User-Agent"] = "OPE LMS";
        headers["Accept-Language"] = "en-US,en;q=0.8";

        QString json = NetworkCall(api_url, "GET", &p, &headers);
        // Convert big id numbers to strings so they parse correctly
        // NOTE: qjsondocument converts ints to doubles and ends up loosing presision
        // find occurences of integer values in json documents and add quotes
        // ("\s*:\s*)(\d+\.?\d*)([^"])|([\[])(\d+\.?\d*)|([,])(\d+\.?\d*)
        // Was picking up digits in the body like $10,000.
        //QRegularExpression regex("(\"\\s*:\\s*)(\\d+\\.?\\d*)([^\"])|([\\[])(\\d+\\.?\\d*)|([,])(\\d+\\.?\\d*)"); //   ":\\s*(\\d+)\\s*,");
        //json = json.replace(regex, "\\1\\4\\6\"\\2\\5\\7\"\\3");  //  :\"\\1\",");
        //qDebug() << "===================================\nParsing http data: " << json;
        QRegularExpression regex("(\\\"\\s*:\\s*)([0-9.]+)(\\s*[,])"); //   ":\\s*(\\d+)\\s*,");
        json = json.replace(regex, "\\1\"\\2\"\\3");  //  :\"\\1\",");

        // Convert response to json
        QJsonParseError *err = new QJsonParseError();
        QJsonDocument doc(QJsonDocument::fromJson(json.toUtf8(), err));
        if (err->error != QJsonParseError::NoError) {
            qDebug() << "\tJSON Parse Err: " << err->errorString() << err->offset;
            qDebug() << "\tJSON Response: " << json;
            qDebug() << "\tJSON Doc: " << doc;
            qDebug() << "\tIs Array: " << doc.isArray();
            qDebug() << "\tIs Object: " << doc.isObject();
            qDebug() << "\tIs nullptr: " << doc.isNull();
        }
        delete err;


        if (doc.isArray()) {
            qDebug() << "\tQuiz Question for Quiz: " << quiz_id;

            // Should be an array of quiz questions
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a quiz question
                QJsonObject o = val.toObject();

                QString id = o["id"].toString("");
                //qDebug() << "Quiz question ID " << id;

                model->setFilter("id = " + id);
                model->select();
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update with current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating quiz question..." << id;
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting quiz..." << id;
                }
                ret += "\n\tProcessing Question: " + QString(id);

                // JSON - list of objects
                /*
NOTE - This comes through the SMC which grabs questions and wrapps them up.

                 */


                record.setValue("id", o["id"].toString(""));
                record.setValue("course_id", course_id);
                record.setValue("quiz_id", o["quiz_id"].toString(""));
                record.setValue("quiz_group_id", o["quiz_group_id"].toString(""));
                record.setValue("assessment_question_id", o["assessment_question_id"].toString(""));
                record.setValue("position", o["position"].toString(""));
                record.setValue("question_type", o["question_type"].toString(""));
                record.setValue("payload_token", o["payload_token"].toString(""));
                // NOTE - To decrypt payload:
                // sha256 hash:  auth_token + course_id + quiz_id + question id + payload_token - use resulting sha256 hash as key
                record.setValue("question_payload", o["question_payload"].toString(""));
                record.setValue("is_active", "true");

                if (is_insert) {
                   model->insertRecord(-1, record);
                } else {
                   // Filter should be set so 0 should be current record
                   model->setRecord(0, record);
                }
                // Write changes
                if(!model->submitAll()) {
                    ret += "\n\t\tError saving quiz! " + QString(id);
                    qDebug() << "ERROR - problem saving quiz " << id << model->lastError();
                }
                model->setFilter(""); // clear the filter

                //qDebug() << "Quiz " << o["name"].toString("");
                model->database().commit();
                //qDebug() << model->lastError();

            }
        } else {
            QString tmp_msg = "ERROR - Unable to pull quiz questions through SMC\n\t- make sure SMC version is >= 1.9.56 and that canvas integration is properly enabled.";
            ret += "\n" + tmp_msg;
            qDebug() << tmp_msg;
        }
    }
    ret += "\nDone pulling quiz questions.";

    return ret;
}


bool EX_Canvas::pullModules()
{
    // Grab modules for each course in the database
    bool ret = false;
    if (_app_db == nullptr) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("modules");

    if (courses_model == nullptr || model == nullptr) {
        qDebug() << "Unable to get models for courses or modules!";
        return false;
    }

    // All enteries should be for this student, so get them all
    courses_model->setFilter("");
    courses_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(courses_model->canFetchMore()) { courses_model->fetchMore(); }

    ret = true;
    int rowCount = courses_model->rowCount();
    for (int i=0; i<rowCount; i++) {
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
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

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
                // {"id":26664700000000088,"name":"Module 1","position":1,"unlock_at":nullptr,
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
                record.setValue("is_active", "true");

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
    if (_app_db == nullptr) { return ret; }

    // Get the list of modules for this student
    GenericTableModel *modules_model = _app_db->getTable("modules");
    GenericTableModel *model = _app_db->getTable("module_items");

    if (modules_model == nullptr || model == nullptr) {
        qDebug() << "Unable to get models for modules or module_items!";
        return false;
    }

    // Get module items for each module
    modules_model->setFilter("");
    modules_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(modules_model->canFetchMore()) { modules_model->fetchMore(); }

    ret = true;
    int rowCount = modules_model->rowCount();
    for (int i=0; i<rowCount; i++) {
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
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

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
                record.setValue("is_active", "true");

                // If this is a page item, make sure it is in the page table too
                if (o["type"].toString("") == "Page") {
                    QString page_url = o["page_url"].toString("");

                    QSqlRecord page_record = pullSinglePage(course_id, page_url);

                    if (page_record.isEmpty()) {
                        ret = false;
                    } else {
                        // Set the content id to the page id
                        record.setValue("content_id", page_record.value("page_id").toString());
                    }
                } else if (o["type"].toString("") == "File") {
                    // This is a File, make sure it is queued so that it will download
                    // even if the "Files" menu isn't
                    QueueCanvasLinkForDownload(o["content_id"].toString(""), course_id, "", o["url"].toString(""));
                }

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
    if (_app_db == nullptr) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("folders");

    if (courses_model == nullptr || model == nullptr) {
        qDebug() << "Unable to get models for courses or folders!";
        return false;
    }

    // Pull all folder info for all courses
    courses_model->setFilter("");
    courses_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(courses_model->canFetchMore()) { courses_model->fetchMore(); }

    ret = true;
    int rowCount = courses_model->rowCount();
    for (int i=0; i<rowCount; i++) {
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
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

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
                // "context_type":"Course","parent_folder_id":nullptr,
                // "created_at":"2018-02-22T21:48:37Z",
                // "updated_at":"2018-02-22T21:48:37Z","lock_at":nullptr,
                // "unlock_at":nullptr,"position":nullptr,"locked":false,
                // "folders_url":"https://canvas.ed/api/v1/folders/999999000000068/folders",
                // "files_url":"https://canvas.ed/api/v1/folders/999999000000068/files",
                // "files_count":0,"folders_count":4,"hidden":nullptr,
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
                record.setValue("is_active", "true");

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
    if (_app_db == nullptr) { return ret; }

    QSqlQuery q;

    // Clear out any empty file entries (no id or name?)
    q.prepare("DELETE FROM files WHERE id='' or filename=''");
    if (!q.exec()) {
        qDebug() << "ERROR RUNNING DB QUERY: " << q.lastQuery() << " - " << q.lastError().text();
        return false;
    } else {
        _app_db->commit();
    }

    // Go through file dl queue - these are links found in content like pages and may not be
    // in the current list
    q.clear();
    q.prepare("SELECT * FROM canvas_dl_queue");
    if (!q.exec()) {
        qDebug() << "ERROR RUNNING DB QUERY: " << q.lastQuery() << " - " << q.lastError().text();
        return false;
    }

    while (q.next()) {
        QString f_id = q.value(1).toString();
        QString course_id = q.value(2).toString();
        QString original_host = q.value(3).toString();
        QString original_url = q.value(4).toString();

        // This will add the file info to the files list so it can be pulled later
        pullSingleCourseFileInfo(f_id, course_id);
    }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");

    if (courses_model == nullptr) {
        qCritical() << "Unable to get models for courses !";
        return false;
    }

    // Mark all files as local_copy_present=4
    // Do this so we can see what is left over when we are done and clear them
    q.prepare("UPDATE files SET local_copy_present='4'");
    if (!q.exec()) {
        qDebug() << "ERROR RUNNING DB QUERY: " << q.lastQuery() << " - " << q.lastError().text();
        return false;
    }


    // Pull all file info for all courses
    courses_model->setFilter("");
    courses_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(courses_model->canFetchMore()) { courses_model->fetchMore(); }

    ret = true;
    int rowCount = courses_model->rowCount();
    for (int i=0; i<rowCount; i++) {
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

                // Pull the file info from canvas
                if (!pullSingleCourseFileInfo(id, course_id)) {
                    // If we fail, mark as false
                    ret = false;
                }
            }
        }
    }

    // Clean up inactive canvas items
    // NOTE - this is the last step before downloading binaries
    clearInactiveItems();

    return ret;
}

bool EX_Canvas::pullSingleCourseFileInfo(QString file_id, QString course_id)
{
    // Grab the file info for this specific file
    bool ret = false;
    if (_app_db == nullptr) { return ret; }

    GenericTableModel *files_model = _app_db->getTable("files");

    if (files_model == nullptr) {
        qCritical() << "Unable to get model for files!";
        return false;
    }

    QHash<QString,QString> params;
    params["per_page"] = "10000"; // Cut down number of api calls significantly
    QJsonDocument doc = CanvasAPICall("/api/v1/files/" + file_id, "GET", &params);

    if (doc.isObject()) {
        // Get file object
        QJsonObject o = doc.object();

        //qDebug() << "Got File Item " << o;

        QString f_id = o["id"].toString("");
        if (f_id == "") {
            qDebug() << "pullSingleCourseFileInfo - INVALID FILE ID " << file_id << "/" << course_id << "  " << o;
            return false;
        }

        // See if this file entry exists in the database
        files_model->setFilter("id=" + file_id);
        files_model->select();
        // NOTE - Make sure to fetch all or we may only get 256 records
        while(files_model->canFetchMore()) { files_model->fetchMore(); }

        QSqlRecord record;
        bool is_insert = false;

        if (files_model->rowCount() >=1) {
            // Row exists - update it
            record = files_model->record(0);
            is_insert = false;
            qDebug() << "\t\tUpdating file info " << file_id << o["display_name"].toString("");
        } else {
            // Inserting new record - need to clear filter
            files_model->setFilter("");
            record = files_model->record();
            is_insert = true;
            qDebug() << "\t\tImporting new file info " << file_id << o["display_name"].toString("");

            // Set some defaults
            record.setValue("pull_file", "");
            record.setValue("local_copy_present", "0");
        }

        // JSON - list of objects
        // {"id":26664700000000097,"folder_id":26664700000000099,
        // "display_name":"101 uses of the quadratic equation.pdf",
        // "filename":"101_uses_of_the_quadratic_equation.pdf",
        // "content-type":"application/pdf",
        // "url":"https://canvas.ed.dev/files/26664700000000097/download?download_frd=1",
        // "size":451941,"created_at":"2017-06-21T21:44:11Z",
        // "updated_at":"2017-06-21T21:44:11Z","unlock_at":nullptr,"locked":false,
        // "hidden":false,"lock_at":nullptr,"hidden_for_user":false,
        // "thumbnail_url":nullptr,"modified_at":"2017-06-21T21:44:11Z",
        // "mime_class":"pdf","media_entry_id":nullptr,"locked_for_user":false}

        record.setValue("id", file_id);
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
        record.setValue("is_active", "true");

       if (is_insert) {
           files_model->insertRecord(-1, record);
       } else {
           // Filter should be set so 0 should be current record
           files_model->setRecord(0, record);
       }

       // Write changes
       if (!files_model->submitAll()) {
           ret = false;
           qDebug() << "*** DB ERROR saving file info " << files_model->lastError().text();
       } else {
           ret = true;
       }

       files_model->setFilter("");
       files_model->database().commit();

    } else {
        qDebug() << "JSON ERROR - got invalid json object " << doc;
    }

    return ret;
}

bool EX_Canvas::pullCourseFilesBinaries()
{
    qDebug() << "----- PULLING CANVAS FILE BINARIES...";
    // Pull binaries for files that are marked as pull
    bool ret = false;
    if (_app_db == nullptr) { return ret; }

    GenericTableModel *files_model = _app_db->getTable("files");

    if (files_model == nullptr) {
        qDebug() << "Unable to get model for files";
        return false;
    }

    //remove file entries if the course doesn't exist.
    QString sql = "delete from files where course_id not in (select id from courses)";
    QSqlQuery q;
    q.prepare(sql);
    if (q.exec() != true) {
        qDebug() << "ERROR clearing orphaned file entries in database " <<
                    q.lastError();
        _app_db->commit();
    }

    files_model->setFilter(""); // pull_file=1
    files_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(files_model->canFetchMore()) { files_model->fetchMore(); }

    qDebug() << "--- Processing DL Files " << files_model->rowCount();

    // Get the local cache folder
    QDir base_dir;
    base_dir.setPath(this->appDataFolder() +
                     "/content/www_root/canvas_file_cache/");
    base_dir.mkpath(base_dir.path());

    ret = true;
    int rowCount = files_model->rowCount();
    for (int i=0; i<rowCount; i++) {
        QSqlRecord f = files_model->record(i);
        QString f_id = f.value("id").toString();
        QString f_filename = f.value("filename").toString();
        QString f_name = f.value("display_name").toString();
        QString content_type = f.value("content_type").toString();
        QString f_url = f.value("url").toString();
        int f_size = f.value("size").toInt();
        QString f_ext = CM_MimeTypes::GetExtentionForMimeType(content_type);
        //QString local_path = "/" + f_id + f_ext; // f.value("pull_file").toString();
        QString local_path = "/" + f_name; // f.value("pull_file").toString();

        // NOTE - Don't rely on mime-type being correct. Pull extension from
        // the filename, and fall back to mime type if extension is empty.
        // FIX for application/x-msdownload - dll, exe and others are reported as
        // same mime-type in canvas
        //QFileInfo finfo(f_filename);
        //if (finfo.completeSuffix() != "") {
        //    local_path = "/" + f_id + "." + finfo.completeSuffix();
        //}

        // Get file type
        f.setValue("pull_file", "/canvas_file_cache" + local_path);

        //if (local_path == "") {
        //    // Assign a new local path
        //    //local_path = "/" + f_id + "_" + f_filename;
        //    local_path = "/" + f_id;
        //    f.setValue("pull_file", local_path);
        //}

        // See if the file already exists locally
        QFileInfo fi = QFileInfo(base_dir.path() + local_path);
        if (fi.exists() && fi.size() == f_size ) {
            qDebug() << "File exists " << local_path; //f_name;
            // Mark it as present
            f.setValue("local_copy_present", "1");
        } else {
            // Download the file
            qDebug() << "Downloading file " << local_path;
            progressCurrentItem = f_filename;
            bool r = DownloadFile(f_url, base_dir.path() + local_path, "Canvas File: " + f_filename);

            if (!r) {
                qDebug() << "ERROR - canvas file download " << f_filename << " - " << f_url;
            } else {
                // Makre the file as present
                f.setValue("local_copy_present", "1");

                // Make sure we save the content header
                /*QHash<QString, QString> headers = web_request->GetAllDownloadHeaders();
                if (headers.contains("Content-Type")) {
                    // Save a file w the mimetype
                    QString mime_local_path = base_dir.path() + local_path + ".mime";
                    QString content_type = headers["Content-Type"];
                    QFile *mime_file = new QFile(mime_local_path);
                    if (mime_file->open(QIODevice::WriteOnly)) {
                        mime_file->write(content_type.toLocal8Bit());
                        mime_file->close();
                    }
                    mime_file->deleteLater();
                }*/
            }
        }

        // Write changes
        files_model->setRecord(i, f);

    }
    files_model->submitAll();
    files_model->database().commit();

    // Clear out any file entries where local_copy_present is 4
    //q.prepare("DELETE FROM files WHERE local_copy_present='4'");
    //if (!q.exec()) {
    //    qDebug() << "ERROR RUNNING DB QUERY: " << q.lastQuery() << " - " << q.lastError().text();
    //    return false;
    //} else {
    //    _app_db->commit();
    //  }

    // Now go through the folder and remove any files that aren't in the file list anymore.
    QDir cache_dir(base_dir);
    qDebug() << "Removing orphaned files:";
    foreach(QString f_name, cache_dir.entryList()) {
        if(f_name == "." || f_name == "..") {
            // Skip these
            continue;
        }
        // See if this file exists in the files database  - NOTE - '' for escaped 's?
        files_model->setFilter("pull_file='/canvas_file_cache/" + f_name.replace("'", "''") + "'");
        files_model->select();
        if (files_model->rowCount() < 1) {
            // File isn't in the database, delete it
            QString local_path = base_dir.path() + "/" + f_name;
            qDebug() << "---- Orphaned File: " << local_path << " - deleting...";

            try {
                QFile::remove(local_path);
            } catch (...) {
                qDebug() << "----- ERROR removing file: " << local_path;
            }

        }
    }

    // Clear old file cache folder
    QDir old_cache_path;
    old_cache_path.setPath(this->appDataFolder() + "/file_cache");
    foreach(QString f_name, old_cache_path.entryList()) {
        if (f_name == "." || f_name == ".." || f_name == "assignment_files") {
            // Skip these
            continue;
        }

        QString local_path = old_cache_path.path() + "/" + f_name;
        qDebug() << "---- Orphaned File: " << local_path << " - deleting...";

        try {
            QFile::remove(local_path);
        } catch (...) {
            qDebug() << "----- ERROR removing file: " << local_path;
        }

    }

    qDebug() << "----- DONE - PULLING CANVAS FILE BINARIES...";

    return ret;
}

bool EX_Canvas::pullCoursePages()
{
    // Grab a list of pages for each course
    qDebug() << "* Starting Pull Course Pages";
    bool ret = false;
    if (_app_db == nullptr) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");

    if (courses_model == nullptr) {
        qDebug() << "!!!Unable to get models for courses or pages!";
        return false;
    }

    // Get the list of pages from canvas
    courses_model->setFilter("");
    courses_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(courses_model->canFetchMore()) { courses_model->fetchMore(); }

    ret = true;
    int rowCount = courses_model->rowCount();
    for (int i=0; i<rowCount; i++) {
        // Get pages for this course
        QSqlRecord course_record = courses_model->record(i);
        QString course_id = course_record.value("id").toString();
        QString course_name = course_record.value("name").toString();
        qDebug() << "\tProcessing Course " << course_id << course_name;
        QHash<QString,QString> p;
        p["per_page"] = "10000"; // Cuts down number of calls significantly
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id + "/pages", "GET", &p);
//qDebug() << "A";
        if (doc.isArray()) {
            qDebug() << "\t\tCanvas Pages for course " << course_id << course_name;
            // Should be an array of pages
            QJsonArray arr = doc.array();
            foreach(QJsonValue val, arr) {
                //qDebug() << "got item...";
                // This should be a module
                QJsonObject o = val.toObject();

                QString id = o["page_id"].toString("");
                QString page_url = o["url"].toString("");
                qDebug() << "\t\t\tFound Page - Pulling Info " << page_url << id;

                QSqlRecord page_record = pullSinglePage(course_id, page_url);
                if (page_record.isEmpty()) {
                    // Error pulling this page?
                    ret = false;
                }
            }
        } else {
            qDebug() << "\t\t!!! Unable to pull array of pages: " << doc;
        }
    }

    return ret;
}

bool EX_Canvas::pullMessages(QString scope)
{
    // Pull the list of conversations, then pull each message in that conversation
    bool ret = false;
    if (_app_db == nullptr) { return ret; }

    if (_app_settings == nullptr) {
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

    if (conversations_model == nullptr || messages_model == nullptr) {
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
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(conversations_model->canFetchMore()) { conversations_model->fetchMore(); }

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
                record.setValue("is_active", "true");

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
                    // NOTE - Make sure to fetch all or we may only get 256 records
                    while(messages_model->canFetchMore()) { messages_model->fetchMore(); }

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
                    record.setValue("is_active", "true");
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
                    if (ret == false) {
                        qDebug() << "ERR Saving message: " << messages_model->lastError();
                    }

                }

            }

            // Commit any remaining transactions
            conversations_model->database().commit();
        }
    }

    _app_db->commit();

    return ret;
}

bool EX_Canvas::pullAssignments()
{
    // Grab assignments for each course in the database
    bool ret = false;
    if (_app_db == nullptr) { return ret; }

    // Get a list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("assignments");

    if (courses_model == nullptr || model == nullptr) {
        qDebug() << "Unable to get models for courses or assignments";
        return false;
    }

    // All entries should be for this student, so get them all
    courses_model->setFilter("");
    courses_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(courses_model->canFetchMore()) { courses_model->fetchMore(); }

    ret = true;
    int rowCount = courses_model->rowCount();
    for(int i=0; i<rowCount; i++) {
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
        //qDebug() << "Is nullptr: " << doc.isnullptr();
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
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

                QSqlRecord record;
                bool is_insert = false;

                if (model->rowCount() == 1) {
                    // Row exists, update w current info
                    record = model->record(0);
                    is_insert = false;
                    qDebug() << "\t\tUpdating assignment..." << id << o["name"].toString("");
                } else {
                    // Need to clear the filter to insert
                    model->setFilter("");
                    record = model->record();
                    is_insert = true;
                    qDebug() << "\t\tImporting assignment..." << id << o["name"].toString("");
                }

                // JSON - list of objects
                // {"id": 35871700000000002,"description": nullptr,"due_at": nullptr,
                // "unlock_at": nullptr,"lock_at": nullptr,"points_possible": nullptr,
                // "grading_type": "points","assignment_group_id": 35871700000000003,
                // "grading_standard_id": nullptr,"created_at": "2017-09-09T23:49:06Z",
                // "updated_at": "2017-09-09T23:49:09Z","peer_reviews": false,
                // "automatic_peer_reviews": false,"position": 1,
                // "grade_group_students_individually": false,"anonymous_peer_reviews": false,
                // "group_category_id": nullptr,"post_to_sis": false,
                // "moderated_grading": false,"omit_from_final_grade": false,
                // "intra_group_peer_reviews": false,
                // "secure_params": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsdGlfYXNzaWdubWVudF9pZCI6IjFjNTBhOTAzLWZmMWMtNDk5My1hYjg3LTY2ZWU2NWViMjY1ZiJ9.4EbPTYlKDiTZps_MxzKTlTCpXuqmzdRW7Z-q1LJX0kg",
                // "course_id": 35871700000000003,"name": "Test Assignment",
                // "submission_types": ["none"],
                // "has_submitted_submissions": false,"due_date_required": false,
                // "max_name_length": 255,"in_closed_grading_period": false,
                // "is_quiz_assignment": false,"muted": false,
                // "html_url": "https://canvas.ed/courses/35871700000000003/assignments/35871700000000002",
                // "has_overrides": false,"needs_grading_count": 0,"integration_id": nullptr,
                // "integration_data": {},"published": true,"unpublishable": true,
                // "only_visible_to_overrides": false,"locked_for_user": false,
                // "submissions_download_url": "https://canvas.ed/courses/35871700000000003/assignments/35871700000000002/submissions?zip=1"
                //  },

                QString desc = o["description"].toString("");
                // Convert SMC Video/Document/Etc links to local links
                desc = ProcessAllLinks(desc);

                record.setValue("id", o["id"].toString(""));
                record.setValue("description", desc);
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
                record.setValue("is_active", "true");

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
    if (_app_db == nullptr) { return ret; }

    // Get the list of courses for this student
    GenericTableModel *courses_model = _app_db->getTable("courses");
    GenericTableModel *model = _app_db->getTable("announcements");

    if (courses_model == nullptr || model == nullptr) {
        qDebug() << "Unable to get models for courses or announcements!";
        return false;
    }

    // Pull all announcements for all courses
    courses_model->setFilter("");
    courses_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(courses_model->canFetchMore()) { courses_model->fetchMore(); }

    ret = true;
    int rowCount = courses_model->rowCount();
    for (int i=0; i<rowCount; i++) {
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
                // NOTE - Make sure to fetch all or we may only get 256 records
                while(model->canFetchMore()) { model->fetchMore(); }

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
                      // The datetime the topic was posted. If it is nullptr it hasn't been posted yet. (see
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
                      // nullptr.
                      "assignment_id": nullptr,
                      // The datetime to publish the topic (if not right away).
                      "delayed_post_at": nullptr,
                      // Whether this discussion topic is published (true) or draft state (false)
                      "published": true,
                      // The datetime to lock the topic (if ever).
                      "lock_at": nullptr,
                      // Whether or not the discussion is 'closed for comments'.
                      "locked": false,
                      // Whether or not the discussion has been 'pinned' by an instructor
                      "pinned": false,
                      // Whether or not this is locked for the user.
                      "locked_for_user": true,
                      // (Optional) Information for the user about the lock. Present when locked_for_user
                      // is true.
                      "lock_info": nullptr,
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
                      "root_topic_id": nullptr,
                      // If the topic is a podcast topic this is the feed url for the current user.
                      "podcast_url": "/feeds/topics/1/enrollment_1XAcepje4u228rt4mi7Z1oFbRpn3RAkTzuXIGOPe.rss",
                      // The type of discussion. Values are 'side_comment', for discussions that only
                      // allow one level of nested comments, and 'threaded' for fully threaded
                      // discussions.
                      "discussion_type": "side_comment",
                      // The unique identifier of the group category if the topic is a group discussion,
                      // otherwise nullptr.
                      "group_category_id": nullptr,
                      // Array of file attachments.
                      "attachments": nullptr,
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
                record.setValue("is_active", "true");

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

QString EX_Canvas::pushAssignments()
{
    // Make sure we have the list so we can do name lookups
    reloadAssignmentList();

    // Push any submitted assignments back to canvas
    QString ret = "";
    bool had_errors = false;
    QStringList error_list;

    if (_app_db == nullptr) { return "ERROR - No valid _app_db"; }

    QSqlRecord record;
    GenericTableModel *model = nullptr;

    QHash<QString,QString> assignment_push_list;

    // Get a list of assignments waiting to be submitted
    model = _app_db->getTable("assignment_submissions");
    if (!model) {
        qDebug() << "Unable to get assignment_submissions model!";
        return "ERROR - Unable to get assignment_submissions model";
    }

    qDebug() << "-- Pushing assignment submissions...";
    // Find submissions that have no sync date
    model->setFilter("synced_on=''");
    model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(model->canFetchMore()) { model->fetchMore(); }

    int rowCount = model->rowCount();
    for (int i=0; i < rowCount; i++) {
        record = model->record(i);
        qDebug() << "--- Submitting assignment file " << record.value("course_id").toString() << " " << record.value("assignment_id").toString() << " " << record.value("origin_url").toString() << "/" << record.value("queue_url").toString();
        QString course_id = record.value("course_id").toString();
        QString course_name = course_id;
        QString assignment_id = record.value("assignment_id").toString();
        QString assignment_name = assignment_id;
        QString post_file = record.value("queue_url").toString();
        QFileInfo post_file_info(post_file);

        if (_course_list.contains(course_id)) {
            course_name = _course_list[course_id];
        }
        //qDebug() << "COURSE NAME: " << course_name;
        if (_assignment_list.contains(assignment_id)) {
            assignment_name = _assignment_list[assignment_id];
        }

        QString assignment_info = post_file_info.fileName() + " (" + course_name + "/" + assignment_name + ") ";
        progressCurrentItem = "Pushing Assignment: " + assignment_info;
        emit progress(i, rowCount, progressCurrentItem);

        QHash<QString, QString> p;
        QFileInfo fi = QFileInfo(post_file);
        p["name"] = fi.fileName();
        p["size"] = QString::number(fi.size());
        // Let canvas guess the content_type
        //p["content_type"] = CM_MimeTypes::GetMimeType(fi.suffix());
        //if (p["content_type"] == "") {
        //    qDebug() << "UNKNOWN MIME TYPE " << fi.fileName();
        //    p["content_type"] = "application/octet-stream";
        //}


        // Post to the canvas server
        // Get upload link
        QJsonDocument doc = CanvasAPICall("/api/v1/courses/" + course_id
                        + "/assignments/" + assignment_id
                        + "/submissions/self/files", "POST", &p);

        /* Should return JSON with something like this
         *
         * {
         *   "upload_url": "https://some-bucket.s3.amazonaws.com/",
         *   "upload_params": {
         *   "key": "/users/1234/files/profile_pic.jpg",
         *   <unspecified parameters; key above will not necesarily be present either>
         * }
        */
        qDebug() << "$$$ SUBMIT STEP 1 RESPONSE: " << last_web_response;

        // Should now have the upload link
        if (doc.isObject()) {
            qDebug() << "Building SUMIT STEP 2 Response...";
            p.clear();
            QJsonObject o = doc.object();
            if (!o.contains("upload_url") || !o.contains("upload_params")) {
                qDebug() << "*** ASSIGNMENT UPLOAD ERROR! missing upload_url "
                         << assignment_id << "\n" << doc.toJson();
                assignment_push_list[post_file] = " - <span class='failed'>Error></span> " + assignment_info + " - No upload_url recieved from canvas server (Step 2 failed)";
                // Jump to next assignment
                continue;
            }
            QString next_url = o["upload_url"].toString();
            QJsonObject params = o["upload_params"].toObject();
            // Copy the provided parameters into the next request
            int order = 65; // Start at ascii a - need this to sort the keys later
            // or canvas will have a problem
            foreach(QString key, params.keys()) {
                p["___" + QString(order) + "_" + key] = params[key].toString();
                order++;
            }
            // Do the actual file upload - NOTE - this will send back a redirect?
            // NOTE2 - NetworkCall will auto follow location redirect so we should
            // get json response from
            qDebug() << "Sending SUBMIT STEP 2 " << next_url;
            QJsonDocument doc2 = CanvasAPICall(next_url, "POST", &p,
                            "multipart/form-data", post_file);
            qDebug() << "$$$ Last Web Response: " << last_web_response;
            if (doc2.isObject()) {
                // Will end up with a 201 or 301 and location header to follow
                // NetworkCall will see that and follow the link

                // Pull the file id
                QJsonObject o = doc2.object();
                QString file_id = o["id"].toString("");
                QString file_url = o["url"].toString("");
                QString content_type = o["content-type"].toString("");
                QString display_name = o["display_name"].toString("");
                QString file_size = o["size"].toString("");

                if (file_id == "") {
                    qDebug() << "*** ERROR - No file id returned on step 2 - pushing assinment! " << assignment_name << assignment_id;
                    assignment_push_list[post_file] = " - <span class='failed'>Error</span>" + assignment_info + " - No file id returned from canvas assignment upload! ";
                    // Jump to next assignment
                    continue;
                }


                // We should now have a json object with a file id, we need
                // to link it to the assignment so it shows up for the teacher
                p.clear();
                // Docs here - https://canvas.instructure.com/doc/api/submissions.html
                p["comment[text_comment]"] = "Submitted via OPE LMS App";
                p["submission[submission_type]"] = "online_upload";
                p["submission[file_ids][]"] = file_id;
                QJsonDocument doc3 = CanvasAPICall("/api/v1/courses/" + course_id
                        + "/assignments/" + assignment_id
                        + "/submissions", "POST", &p);
                if (doc3.isObject()) {
                    // Check if valid submission
                    QJsonObject doc3_object = doc3.object();
                    QJsonArray attachments_arr = doc3_object["attachments"].toArray();
                    QString upload_success = attachments_arr.first().toObject()["upload_status"].toString("");

                    qDebug() << "Assignment pushed - TODO" << doc3.toJson();

                    if (upload_success == "success") {
                        // Mark that the assignment has been synced so we don't try to
                        // upload it again.
                        record.setValue("synced_on", QDateTime::currentDateTime().toString());
                        model->setRecord(i, record);

                        assignment_push_list[post_file] = " - <span class='accepted'>SUCCESS</span> " + assignment_info;
                    } else {
                        assignment_push_list[post_file] = " - <span class='failed'>FAILED</span> " + assignment_info;
                        qDebug() << "ERROR - Final step linking assignment failed " << doc3.toJson();
                        had_errors = true;
                    }


                } else {
                    QString err = assignment_info + " - ERROR - Problem linking uploaded file with assignment " + assignment_id;
                    qDebug() << err << " --- " << doc3.toJson();
                    assignment_push_list[post_file] = " - <span class='failed'>Error</span> " + assignment_info + " - Problem linking uploaded file with assignment " + assignment_id;
                    had_errors = true;
                }

            } else {
                // Invalid response??
                QString err = assignment_info + " - ERROR - *** ASSIGNMENT UPLOAD ERROR!! - Invalid response for upload link! " + assignment_id;
                qDebug() << err << " -- " << doc2.toJson();
                had_errors = true;
                assignment_push_list[post_file] = " - <span class='failed'>Error</span> " + assignment_info + " - *** ASSIGNMENT UPLOAD ERROR!! - Invalid response for upload link! " + assignment_id;
                continue; // Jump to next assignmment
            }

        } else {
            QString err =  assignment_info + " ERROR - ASSIGNMENT UPLOAD ERROR!!! - Invalid json object: pushAssignments " + assignment_id;
            qDebug() << err << " -- " << doc.toJson();
            assignment_push_list[post_file] = " - <span class='failed'>Error</span> " + assignment_info + " - ASSIGNMENT UPLOAD ERROR!!! - Invalid json object: pushAssignments " + assignment_id;
            had_errors = true;
        }
    }
    bool submit_sucess = model->submitAll();
    if (!submit_sucess) {
        qDebug() << "DB ERROR: "  << model->lastError();
        return "ERROR - Unable to submit changes to database!";
    }

    // NOTE - May fail if commit not started, that is ok.
    model->database().commit();

    foreach(QString key, assignment_push_list.keys()) {
        ret += assignment_push_list[key] + "\n";
    }
    if (assignment_push_list.count() == 0) {
        ret += " - No assignments to push";
    }

    if (had_errors) {
        ret += "\n **** <span class='failed'>Error</span> **** - One or more assignments failed to properly submit!";
    }

    progressCurrentItem = "";
    //emit progress(i, rowCount, progressCurrentItem);

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
    if (_app_db == nullptr) { return false; }
    QSqlRecord record;
    GenericTableModel *model = nullptr;

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
            cache_path.setPath(this->appDataFolder() + "/file_cache/assignment_files");
            // Make sure the base folder exists
            cache_path.mkpath(cache_path.path());

            QFileInfo fi = QFileInfo(file_url);

            QString tmp_file = QString::number(QDateTime::currentSecsSinceEpoch()) + "_" +fi.fileName();

            QString tmp_file_path = cache_path.absolutePath() + "/" + tmp_file;
            // Copy file to temp location
            QFile::copy(file_url, tmp_file_path);

            // Add the submission to the database
            model = _app_db->getTable("assignment_submissions");
            if (model == nullptr) {
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
    // return false;
}


bool EX_Canvas::LinkToCanvas(QString redirect_url, QString client_id)
{
    // Redirect to canvas server to authorize this app

    //// TODO add purpose to key generation? &purpose=MobileLMS
    // Open the browser. We will get an event from the web server when it is done
    // https://lms.dev.domain.com/login/oauth2/auth?client_id=10&response_type=code&redirect_uri=urn:ietf:wg:oauth:2.0:oob
    //QString canvas_url = canvas_url;
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

    QString response_string = NetworkCall(canvas_url + "/login/oauth2/token", "POST", &params, &headers);
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


QJsonDocument EX_Canvas::CanvasAPICall(QString api_call, QString method, QHash<QString, QString> *p, QString content_type, QString post_file, bool expect_non_json_answer)
{
    // Network call will recursivly call the canvas api until it runs out of link headers
    QHash<QString,QString> headers;
    headers["Authorization"] = "Bearer " + canvas_access_token;
    headers["User-Agent"] = "OPE LMS";
    headers["Accept-Language"] = "en-US,en;q=0.8";

    QString call_url = api_call;
    // Don't append canvas server if full address is already present
    if (!api_call.toLower().startsWith("http")) {
        call_url = canvas_url;
        if (call_url.endsWith("/") != true) {
            call_url += "/";
        }
        if (api_call.startsWith("/")) {
            // cut off beginning / in url
            api_call = api_call.mid(1);
        }
        call_url = call_url + api_call;
    }

    QString json = NetworkCall(call_url, method, p, &headers, content_type, post_file);
//qDebug() << "C";
    //if (call_url == "https://canvas.ed/api/v1/courses/21647000000049/pages/class-introduction") {
    //    qDebug() << "PRE JSON RESPONSE: " << json;
    //}

    //http_reply_data = "{\"default_time_zone\":\"Pacific Time (US \u0026 Canada)\",\"id\":1,\"name\":\"Admin\",\"parent_account_id\":nullptr,\"root_account_id\":nullptr,\"default_storage_quota_mb\":5000,\"default_user_storage_quota_mb\":50}";

    // Convert big id numbers to strings so they parse correctly
    // NOTE: qjsondocument converts ints to doubles and ends up loosing presision
    // find occurences of integer values in json documents and add quotes
    // ("\s*:\s*)(\d+\.?\d*)([^"])|([\[])(\d+\.?\d*)|([,])(\d+\.?\d*)
    // Was picking up digits in the body like $10,000.
    //QRegularExpression regex("(\"\\s*:\\s*)(\\d+\\.?\\d*)([^\"])|([\\[])(\\d+\\.?\\d*)|([,])(\\d+\\.?\\d*)"); //   ":\\s*(\\d+)\\s*,");
    //json = json.replace(regex, "\\1\\4\\6\"\\2\\5\\7\"\\3");  //  :\"\\1\",");
    //qDebug() << "===================================\nParsing http data: " << json;
    QRegularExpression regex("(\\\"\\s*:\\s*)([0-9.]+)(\\s*[,])"); //   ":\\s*(\\d+)\\s*,");
    json = json.replace(regex, "\\1\"\\2\"\\3");  //  :\"\\1\",");

    //if (call_url == "https://canvas.ed/api/v1/courses/21647000000049/pages/class-introduction") {
    //    qDebug() << "POST JSON RESPONSE: " << json;
    //}

    // Convert response to json
    QJsonParseError *err = new QJsonParseError();
    QJsonDocument d(QJsonDocument::fromJson(json.toUtf8(), err));
    if (err->error != QJsonParseError::NoError && expect_non_json_answer != true) {
        qDebug() << "\tJSON Parse Err: " << err->errorString() << err->offset;
        qDebug() << "\tJSON Response: " << json;
        qDebug() << "\tJSON Doc: " << d;
        qDebug() << "\tIs Array: " << d.isArray();
        qDebug() << "\tIs Object: " << d.isObject();
        qDebug() << "\tIs nullptr: " << d.isNull();
    }

    delete err;
    return d;
}

QString EX_Canvas::NetworkCall(QString url, QString method, QHash<QString, QString> *p, QHash<QString, QString> *headers, QString content_type, QString post_file)
{
    QString ret;
//qDebug() << "BA";
    last_web_response = web_request->NetworkCall(url, method, p, headers, content_type, post_file);
//qDebug() << "BB";
    ret = last_web_response;
    //QByteArray bin_ret = web_request->NetworkCall(url, method, p, headers);
    //ret = QString::fromUtf8(bin_ret);

    // If this is a file push - canvas needs us to follow the 301. 201 response is just done
    // that should be set in the location header
    QString location_header = web_request->GetHeader("Location");
    int status_code = web_request->httpStatusCode();
    qDebug() << url << " - " << status_code << " " << location_header;
    if ((status_code == 201 || status_code >= 301 || status_code == 302 || status_code == 307 || status_code == 308 ) &&
            (method.toUpper() == "POST" || method.toUpper() == "PUT") &&
            location_header != "" && location_header.toLower().contains("/create_success?") ) {
        qDebug() << "### FOLLOWING Location Header from " << url << " to " <<  location_header;
        // Hit the next link
        headers->clear();
        (*headers)["Authorization"] = "Bearer " + canvas_access_token;
        (*headers)["User-Agent"] = "OPE LMS";
        (*headers)["Accept-Language"] = "en-US,en;q=0.8";
        p->clear();
        qDebug() << "First RET: " << ret;
        // Follow up changed to GET as specified in the docs under "Confirm upload success"
        // https://canvas.instructure.com/doc/api/file.file_uploads.html
        last_web_response = web_request->NetworkCall(location_header, "GET", p, headers);
        ret = last_web_response;
        qDebug() << "2nd RET: " << ret;
        return ret;
    }

    QString link_header = web_request->GetHeader("Link");
    bool follow_link = false;

    // For multiple pages - we follow the link header to the next page automatically
    if (link_header != "")
    {
        follow_link = true;
    }

    while(follow_link == true) {

        // TODO - Need to keep following link until we run out of pages!!!
        //qDebug() << "Link header: " << link_header;
        QString next_url = "";
        QStringList parts = link_header.split(",", Qt::SkipEmptyParts);
        foreach (QString item, parts)
        {
            if(item.contains("rel=\"next\""))
            {
                // Get the link
                QStringList parts2 = item.split(";", Qt::SkipEmptyParts);
                next_url = parts2[0]; // Should be the first item.
                next_url = next_url.replace("<", "").replace(">", ""); // strip off the <> tags
            }
        }

        // If there is a link header, we need to call NetworkCall recursively to get the next chunk
        if (next_url != "")
        {
            qDebug() << "--> Nested API call: " << next_url;
            QString next = web_request->NetworkCall(next_url, method, p, headers, content_type, post_file);
            // Make sure to save the current link header for this page
            link_header = web_request->GetHeader("Link");
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

        } else {
            // Out of next links, stop following them
            follow_link = false;
        }

    }

    return ret;
}

bool EX_Canvas::DownloadFile(QString url, QString local_path, QString item_name)
{
    progressCurrentItem = item_name;
    emit progress(0, 0, progressCurrentItem);
    int count = 0;
    int dl_tries = 2;
    while (count < dl_tries) {
        // Try 2 times to download each file
        //qDebug() << " - DL Try " << count << url;
        if (web_request->DownloadFile(url, local_path) == true) {
            // DL worked, done.
            return true;
        }
        // DL failed, try again?
        count++;
    }

    qDebug() << " ***** ERROR downloading file after " << count << " tries: " << url;
    return false;
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

void EX_Canvas::SetCanvasURL(QString url)
{
    canvas_url = url;
}

QString EX_Canvas::ProcessAllLinks(QString content)
{
    QString ret = content;
    ret = ProcessDownloadLinks(ret);
    ret = ProcessSMCDocuments(ret);
    ret = ProcessSMCVideos(ret);
    ret = ProcessPagesLinks(ret);

    return ret;
}

QString EX_Canvas::ProcessSMCVideos(QString content)
{
    QString ret = content;
    // Search content for any SMC links
    // <iframe width="650" height="405" src="https://smc.ed/media/player.load/6bc33efb174248c5bfff9cdd5f986ae9?autoplay=true" frameborder="0" allowfullscreen></iframe>
    // https://smc.ed/media/player.load/6bc33efb174248c5bfff9cdd5f986ae9

    QHash<QString, QStringList> replace_urls;

    QRegExp rx;

    // Find iframes
    // [\"']{1}\s?((https?:\/\/[a-zA-Z\.0-9:]*)\/media\/player(\.load)?\/([a-zA-Z0-9]+)(\/)?(\?)?(autoplay=(true|false))?)\s*[\"']{1}
    rx.setPattern("[\\\"']{1}\\s?((https?:\\/\\/[a-zA-Z\\.0-9:]*)\\/media\\/player(\\.load)?\\/([a-zA-Z0-9]+)(\\/)?(\\?)?(autoplay=(true|false))?)\\s*[\\\"']{1}");

    // rx.cap(0) = full match
    // 1 = full url - https://smc.ed/media/player.load/3f0s98foeu/
    // 2 = server - https://smc.ed
    // 3 = if .load if present or empty if not
    // 4 = movie id

    //"href=http(s)://.../media/player[.load]/???..."
    int pos = 0;
    while ((pos = rx.indexIn(ret, pos)) != -1) {
        pos += rx.matchedLength();

        // Get the full URL for this item
        QString full_url = rx.cap(1);
        // Get the host for this link
        QString smc_host = rx.cap(2);
        // Get the movie ID for this link
        QString movie_id = rx.cap(4);
        // Add to the list to be downloaded
        if (!_localhost_url.startsWith(smc_host)) {
            replace_urls[movie_id] = QStringList() << smc_host << full_url;
        } else {
            // This link already points to a local host address?
            qDebug() << "-- Link found w localhost address? " << full_url;
        }

    }

    qDebug() << "Found SMC video links";
    qDebug() << replace_urls;

    // Queue up video to be downloaded
    foreach (QString movie_id, replace_urls.keys()) {
        QStringList values = replace_urls[movie_id];
        QString original_host = values[0];
        QString original_url = values[1];

        QueueVideoForDownload(movie_id, original_host, original_url);
    }

    // Replace old URLs w the new ones
    foreach (QString movie_id, replace_urls.keys()) {
        QStringList values = replace_urls[movie_id];
        QString original_host = values[0];
        QString original_url = values[1];
        QString new_url = _localhost_url;
        new_url += "/player.html?movie_id=" + movie_id;
        qDebug() << "Replacing " << original_url << " with " << new_url;
        ret = ret.replace(original_url, new_url, Qt::CaseInsensitive);
    }

    return ret;
}

QString EX_Canvas::ProcessSMCDocuments(QString content)
{
    QString ret = content;

    // Search for any SMC Document links
    // <iframe src="https://smc.ed/smc/static/ViewerJS/index.html#/media/dl_document/4c3b4f9275bf4ff699b2dc98079f761b" width="734" height="620" allowfullscreen="allowfullscreen" webkitallowfullscreen="webkitallowfullscreen"></iframe>
    // https://smc.ed/media/dl_document/4c3b4f9275bf4ff699b2dc98079f761b

    QHash<QString, QStringList> replace_urls;

    QRegExp rx;

    // Find URLS
    // "((https?:\\/\\/[a-zA-Z\\.0-9:]*)((\\/smc)?\\/static\\/ViewerJS\\/index.html#)?\\/media\\/dl_document\\/([a-zA-Z0-9]+))"
    rx.setPattern("((https?:\\/\\/[a-zA-Z\\.0-9:]*)((\\/smc)?\\/static\\/ViewerJS\\/index.html#)?\\/media\\/dl_document\\/([a-zA-Z0-9]+))");

    // rx.cap(0) = full match
    // 1 = https://smc.ed/media/dl_document/4c3b4f9275bf4ff699b2dc98079f761b
    // 2 = server - https://smc.ed
    // 3 = /smc/static/ViewerJS/index.html# (if exists)
    // 4 = /smc (if exists)
    // 5 = document id

    int pos = 0;
    while ((pos = rx.indexIn(ret, pos)) != -1) {
        pos += rx.matchedLength();

        // Get the full URL for this item
        QString full_url = rx.cap(1);
        // Get the host for this item
        QString smc_host = rx.cap(2);
        // Get the document id for this item
        QString document_id = rx.cap(5);

        // Add to the list to be downloaded
        if (!_localhost_url.startsWith(smc_host)) {
            replace_urls[full_url] = QStringList() << smc_host << document_id;
        } else {
            // Link already points to a local host address, don't mess with it
            qDebug() << "-- Link found w localhost address? " << full_url;
         }
    }

    qDebug() << "Found SMC Document links";
    qDebug() << replace_urls;

    // Queue up document to be downloaded
    foreach(QString original_url, replace_urls.keys()) {
        QStringList values = replace_urls[original_url];
        QString original_host = values[0];
        QString document_id = values[1];

        QueueDocumentForDownload(document_id, original_host, original_url);
    }

    // Replace old URLs w the new ones
    foreach(QString original_url, replace_urls.keys()) {
        QStringList values = replace_urls[original_url];
        QString original_host = values[0];
        QString document_id = values[1];
        QString new_url = _localhost_url;
        if (original_url.contains("ViewerJS")) {
            // Use the ViewerJS tool to display this document
            new_url += "/ViewerJS/index.html#/smc_document_cache/" + document_id;
        } else {
            // Not using ViewerJS - make it the direct link to the file
            new_url += "/smc_document_cache/" + document_id;
        }
        qDebug() << "Replacing " << original_url << " with " << new_url;
        ret = ret.replace(original_url, new_url, Qt::CaseInsensitive);
    }

    return ret;
}

QString EX_Canvas::ProcessDownloadLinks(QString content)
{
    QString ret = content;
    // Search content for any file links to canvas files

    // Key will be full_url followed by the list of items
    //replace_urls[full_url] = QStringList() << file_id << course_id << canvas_host;
    QHash<QString, QStringList> replace_urls;

    QRegExp rx;

    // // Example link of image file embedded in this page/text
    // <img src="https://canvas.ed/courses/21647000000303/files/21647000019197/preview" alt="Misleading Graphs_Page_01.jpg" data-api-endpoint="https://canvas.ed/api/v1/courses/21647000000303/files/21647000019197" data-api-returntype="File" />


    // Find download links
    // [\s>'\"]?((https?:\/\/[a-zA-Z\.0-9:]*)?(\/api\/v1)?\/courses\/([0-9]+)\/(files|modules\/items)\/([0-9]+)(\/download|\/preview)?([\?]?[;=&0-9a-zA-Z%_]+)?)[\s<'\"]?
    rx.setPattern("[\\s>'\\\"]?((https?:\\/\\/[a-zA-Z\\.0-9:]*)?(\\/api\\/v1)?\\/courses\\/([0-9]+)\\/(files|modules\\/items)\\/([0-9]+)(\\/download|\\/preview)?([\\?]?[;=&0-9a-zA-Z%_]+)?)[\\s<'\\\"]?");

    // rx.cap(0) = full match
    // 1 = full url - https://smc.ed/media/player.load/3f0s98foeu/
    // 2 = server - https://smc.ed
    // 3 = /api/v1
    // 4 = course id
    // 5 = /files/ or modules/items
    // 6 = file id
    // 7 = /download if present
    // 8 = ? full query string if present

    int pos = 0;
    while ((pos = rx.indexIn(ret, pos)) != -1) {
        // Save the current match - use the position of the url, not the whole match
        // This is important so we don't loose quotes or other whitespace if it exists
        int start_pos = rx.pos(1);
        int match_len = rx.cap(1).length();

        //pos += rx.matchedLength();
        // Use inline replacement later, so always start at pos 0
        pos = 0;

        // Get the full URL for this item
        QString full_url = rx.cap(1);
        qDebug() << "<<<<< FOUND URL " << full_url;
        // Get the host for this link
        QString canvas_host = rx.cap(2);
        if (canvas_host == "") {
            // For relative links - fill in current host
            canvas_host = canvas_url;
        }
        // Get the course id for this link
        QString course_id = rx.cap(4);
        // Get url type (files or modules/items)
        QString canvas_types = rx.cap(5);
        // Get the file id
        QString file_id = rx.cap(6);
        QString module_item_id = "";

        if (canvas_types == "modules/items") {
            // Need to lookup the file_id, this is the module item id
            module_item_id = file_id;
            file_id = "";
            QSqlQuery file_query;
            file_query.prepare("SELECT content_id FROM module_items WHERE id=:item_id");
            file_query.bindValue(":item_id", module_item_id);
            if (!file_query.exec()) {
                qDebug() << "SQL Error - file lookup " << file_query.lastError();
            } else {
                while(file_query.next()) {
                    file_id = file_query.value("content_id").toString();
                }
            }

            if (file_id == "") {
                // didn't find file, move on.
                qDebug() << " *** DB ERROR - couldn't pull module item for " << module_item_id << " " << file_query.lastError() << " - " << full_url;

                // Replace with dummy link so we can move on or we will get stuck in a loop.
                ret = ret.replace(start_pos, match_len, "<INVALID_MODULE_ITEM_" + module_item_id + ">");

                // Jump to next item.
                continue;
            }
        }

        // Add to the list to be downloaded
        if (!_localhost_url.startsWith(canvas_host)) {
            // Add this to the download list later
            QueueCanvasLinkForDownload(file_id, course_id, canvas_host, full_url);

            // Replace this text with the place holder.
            // <CANVAS_FILE_???>  ??? becomes the file id
            QString new_url = "<CANVAS_FILE_" + file_id + ">";

            qDebug() << "Replacing " << full_url << " with " << new_url;
            ret = ret.replace(start_pos, match_len, new_url);
        } else {
            // This link already points to a local host address?
            qDebug() << "-- Link found w localhost address? " << full_url;
        }
    }

    return ret;
}

QString EX_Canvas::ProcessPagesLinks(QString content)
{
    // Find links to canvas pages and change them for local links
    // TODO - links to pages aren't getting translated to local links

    QString ret = content;
    // Example link ot another page (maybe from assignments?)
    // <a id="" title="Misleading Graphs" href="https://canvas.ed/courses/21647000000303/pages/misleading-graphs" target="blank" data-api-endpoint="https://canvas.ed/api/v1/courses/21647000000303/pages/misleading-graphs" data-api-returntype="Page">Misleading Graphs</a>


    return ret;
}

bool EX_Canvas::updateDownloadLinks()
{
    qDebug() << ">> Updating download links...";

    // Replace <CANVAS_FILE_???> tags with real links
    QSqlQuery q;
    q.prepare("SELECT * FROM files");

    if (!q.exec()) {
        qDebug() << "SQL Error!! " << q.lastError();
        return false;
    }

    while(q.next()) {
        QString file_id = q.value("id").toString();
        QString file_name = q.value("filename").toString();
        QString pull_file = q.value("pull_file").toString();
        QString content_type = q.value("content_type").toString();
        QString f_ext = CM_MimeTypes::GetExtentionForMimeType(content_type);

        QString file_tag = "<CANVAS_FILE_" + file_id + ">";
        //QString new_url = _localhost_url + "/canvas_file_cache/" + file_id + f_ext;
        // QString new_url = _localhost_url + "/canvas_file_cache/" + file_name;
        QString new_url = _localhost_url + pull_file;

        qDebug() << "Replacing " << file_tag << " with " << new_url;

        // Change in tables: assignments, pages
        QString sql = "UPDATE assignments SET description=REPLACE(description, :file_tag, :new_url)";
        QSqlQuery q2;
        q2.prepare(sql);
        q2.bindValue(":file_tag", file_tag);
        q2.bindValue(":new_url", new_url);
        if (!q2.exec()) {
            qDebug() << "SQL Error!! " << q2.lastError() << " on " << q2.lastQuery();
        }

        sql = "UPDATE pages SET body=REPLACE(body, :file_tag, :new_url)";
        QSqlQuery q3;
        q3.prepare(sql);
        q3.bindValue(":file_tag", file_tag);
        q3.bindValue(":new_url", new_url);
        if(!q3.exec()) {
            qDebug() << "SQL Error!! " << q3.lastError() << " on " << q3.lastQuery();
        }

        // Write changes to db
        _app_db->commit();
    }

    return true;
 }

bool EX_Canvas::QueueVideoForDownload(QString movie_id, QString original_host, QString original_url)
{
    // Add the video id to the list for downloading
    bool ret = false;

    QSqlQuery q;
    q.prepare("SELECT count(media_id) FROM smc_media_dl_queue2 WHERE media_id = :media_id");
    q.bindValue(":media_id", movie_id);

    if(q.exec()) {
        q.next();
        int count = q.value(0).toInt();
        if (count < 1) {
            // ID isn't in the list
            QSqlQuery q2;
            q2.prepare("INSERT INTO smc_media_dl_queue2 (`id`, `media_id`, `original_host`, `original_url`) VALUES (NULL, :media_id, :original_host, :original_url)");
            q2.bindValue(":media_id", movie_id);
            q2.bindValue(":original_host", original_host);
            q2.bindValue(":original_url", original_url);
            q2.exec();
            qDebug() << "New Movie ID " << movie_id;
        } else {
            // Is in the list, update it
            qDebug() << "Movie ID already queued " << movie_id;
            QSqlQuery q3;
            q3.prepare("UPDATE smc_media_dl_queue2 SET `original_host`=:original_host, `original_url`=:original_url WHERE `media_id`=:media_id");
            q3.bindValue(":original_host", original_host);
            q3.bindValue(":original_url", original_url);
            q3.bindValue(":media_id", movie_id);
            q3.exec();
        }
        ret = true;

    } else {
        // Error running query
        qDebug() << "ERROR RUNNING QUERY: " << q.lastError().text();
        ret = false;
    }

    return ret;
}

bool EX_Canvas::QueueDocumentForDownload(QString document_id, QString original_host, QString original_url)
{
    // Add the document id to the list for downloading
    bool ret = false;

    QSqlQuery q;
    q.prepare("SELECT count(document_id) FROM smc_document_dl_queue2 WHERE document_id = :document_id");
    q.bindValue(":document_id", document_id);

    if(q.exec()) {
        q.next();
        int count = q.value(0).toInt();
        if (count < 1) {
            // ID isn't in the list
            QSqlQuery q2;
            q2.prepare("INSERT INTO smc_document_dl_queue2 (`id`, `document_id`, `original_host`, `original_url`) VALUES (NULL, :document_id, :original_host, :original_url)");
            q2.bindValue(":document_id", document_id);
            q2.bindValue(":original_host", original_host);
            q2.bindValue(":original_url", original_url);
            q2.exec();
            qDebug() << "New Document ID " << document_id;
        } else {
            qDebug() << "Document ID already queued " << document_id;
        }
        ret = true;

    } else {
        // Error running query
        qDebug() << "ERROR RUNNING QUERY: " << q.lastError().text();
        ret = false;
    }

    return ret;
}

bool EX_Canvas::QueueCanvasLinkForDownload(QString file_id, QString course_id, QString original_host, QString original_url)
{
    // Add the file id to the list for downloading
    bool ret = false;

    if (_app_db == nullptr) {
        qCritical() << "Invalid app DB ";
        return false;
    }

    QSqlQuery q;
    q.prepare("SELECT count(file_id) FROM canvas_dl_queue WHERE file_id = :file_id");
    q.bindValue(":file_id", file_id);

    if(q.exec()) {
        q.next();
        int count = q.value(0).toInt();
        if (count < 1) {
            // ID isn't in the list
            QSqlQuery q2;
            q2.prepare("INSERT INTO canvas_dl_queue (`id`, `file_id`, `course_id`, `original_host`, `original_url`) VALUES (NULL, :file_id, :course_id, :original_host, :original_url)");
            q2.bindValue(":file_id", file_id);
            q2.bindValue(":course_id", course_id);
            q2.bindValue(":original_host", original_host);
            q2.bindValue(":original_url", original_url);
            q2.exec();

            qDebug() << "New File ID " << file_id;
        } else {
            QSqlQuery q2;
            q2.prepare("UPDATE canvas_dl_queue SET course_id=:course_id, original_host=:original_host, original_url=:original_url WHERE file_id=:file_id");
            q2.bindValue(":course_id", course_id);
            q2.bindValue(":original_host", original_host);
            q2.bindValue(":original_url", original_url);
            q2.bindValue(":file_id", file_id);
            q2.exec();

            qDebug() << "File ID already queued " << file_id;
        }

        ret = true;

    } else {
        // Error running query
        qDebug() << "ERROR RUNNING QUERY: " << q.lastError().text();
        ret = false;
    }

    return ret;
}

bool EX_Canvas::pullSMCVideos()
{
    bool ret = false;

    // Make sure our cache path exists
    // Get the local cache folder
    QDir base_dir;
    base_dir.setPath(this->appDataFolder() + "/content/www_root/smc_video_cache/");
    base_dir.mkpath(base_dir.path());

    // Get list of video IDs
    QSqlQuery q;
    q.prepare("SELECT * FROM smc_media_dl_queue2");
    if(!q.exec()) {
        qDebug() << "ERROR RUNNING DB QUERY: " << q.lastQuery() << " - " << q.lastError().text();
        return false;
    }
    while(q.next()) {
        // See if this file exists
        QString video_id = q.value(1).toString();
        QString local_path = base_dir.path() + "/" + video_id + ".mp4";
        QFileInfo fi = QFileInfo(local_path);
        if (fi.exists() && fi.size() > 1000) {
            qDebug() << " - SMC Video File already downloaded: " << local_path;
        } else {
            qDebug() << "** Need to download video file " << local_path;
            // Get the original host
            QString smc_url = q.value(2).toString();  //_app_settings->value("smc_url", "https://smc.ed").toString();
            // Build the download url
            smc_url += "/media/dl_media/" + video_id + "/mp4";

            bool r = DownloadFile(smc_url, local_path, "SMC Video: " + video_id);
            if (!r) {
                qDebug() << "Error downloading file " << smc_url;
            }
        }
        // Now pull poster image
        local_path = base_dir.path() + "/" + video_id + ".poster.png";
        fi = QFileInfo(local_path);
        if (fi.exists() && fi.size() > 1000) {
            qDebug() << " - SMC Video Poster file already downloaded: " << local_path;
        } else {
            qDebug() << "** Need to download poster file " << local_path;
            QString smc_url = q.value(2).toString(); // _app_settings->value("smc_url", "https://smc.ed").toString();
            // Grab the first 2 characters of the ID
            QString prefix = video_id.mid(0,2);
            smc_url += "/static/media/" + prefix + "/" + video_id + ".poster.png";
            bool r = DownloadFile(smc_url, local_path, "SMC Poster: " + video_id);
            if (!r) {
                qDebug() << "Error downloading poster file " << smc_url;
            }
        }
    }

    // Now go through the folder and remove any files that aren't in the file list anymore.
    QDir cache_dir(base_dir);
    qDebug() << "Removing orphaned SMC Media files:";
    foreach(QString f_name, cache_dir.entryList()) {
        if(f_name == "." || f_name == "..") {
            // Skip these
            continue;
        }
        // See if this file exists in the files database
        QFileInfo fi(f_name);
        QString base_name = fi.baseName();
        //qDebug() << " Checknig SMC media file " << base_name;
        QSqlQuery q;

        q.prepare("select count(media_id) as cnt from smc_media_dl_queue2 where media_id=:media_id");
        q.bindValue(":media_id", base_name);
        if (!q.exec()) {
            qDebug() << "DB ERROR - PullSMCVideos " << q.lastError();
        } else {
            q.next();
            QSqlRecord r = q.record();
            int size = r.value(0).toInt();
            //qDebug() << "------ FOUND " << size << " records";
            if(size < 1) {
                //qDebug() << "Deleting Orphaned SMC Video " << f_name;

                // File isn't in the database, delete it
                QString local_path = base_dir.path() + "/" + f_name;
                qDebug() << "---- Orphaned SMC Video File: " << local_path << " - deleting...";

                try {
                    QFile::remove(local_path);
                } catch (...) {
                    qDebug() << "----- ERROR removing file: " << local_path;
                }
            }
        }
    }

    ret = true;

    return ret;
}

bool EX_Canvas::pullSMCDocuments()
{
    bool ret = false;

    // Make sure our cache path exists
    QDir base_dir;
    base_dir.setPath(this->appDataFolder() + "/content/www_root/smc_document_cache/");
    base_dir.mkpath(base_dir.path());

    // Get the list of document ids
    QSqlQuery q;
    q.prepare("SELECT * from smc_document_dl_queue2");
    if (!q.exec()) {
        qDebug() << "ERROR RUNNING DB QUERY: " << q.lastQuery() << " - " << q.lastError().text();
        return false;
    }

    while(q.next()) {
        // See if document exists
        QString document_id = q.value(1).toString();
        QString local_path = base_dir.path() + "/" + document_id; // TODO - need file extension?
        QFileInfo fi = QFileInfo(local_path);
        if (fi.exists() && fi.size() > 10) {
            qDebug() << " - SMC Document file already downloaded: " << local_path;
        } else {
            qDebug() << "** Need to download document file " << local_path;
            QString smc_url = q.value(2).toString();
            // Build dl url
            smc_url += "/media/dl_document/" + document_id;
            bool r = DownloadFile(smc_url, local_path, "SMC Document: " + document_id);
            if (!r) {
                qDebug() << "Error downloading file " << smc_url;
            } else {
                // File downloaded, get the content type header
                QHash<QString, QString> headers = web_request->GetAllDownloadHeaders();
                if (headers.contains("Content-Type")) {
                    // Save a file with the mime type
                    QString mime_local_path = local_path + ".mime";
                    QString content_type = headers["Content-Type"];
                    QFile *mime_file = new QFile(mime_local_path);
                    if (mime_file->open(QIODevice::WriteOnly)) {
                        mime_file->write(content_type.toLocal8Bit());
                        mime_file->close();
                    }
                    mime_file->deleteLater();
                }
            }
        }
    }

    // Now go through the folder and remove any files that aren't in the file list anymore.
    QDir cache_dir(base_dir);
    qDebug() << "Removing orphaned SMC Media files:";
    foreach(QString f_name, cache_dir.entryList()) {
        if(f_name == "." || f_name == "..") {
            // Skip these
            continue;
        }
        // See if this file exists in the files database
        QFileInfo fi(f_name);
        QString base_name = fi.baseName();
        QSqlQuery q;
        q.prepare("SELECT COUNT(document_id) as cnt FROM smc_document_dl_queue2 where document_id=:document_id");
        q.bindValue(":document_id", base_name);
        if (!q.exec()) {
            qDebug() << "DB ERROR - PullSMCDocuments " << q.lastError();
        } else {
            q.next();
            QSqlRecord r = q.record();
            int size = r.value(0).toInt();
            //qDebug() << "------ FOUND " << size << " records";
            if(size < 1) {
                //qDebug() << "Deleting Orphaned SMC Document " << f_name;

                // File isn't in the database, delete it
                QString local_path = base_dir.path() + "/" + f_name;
                qDebug() << "---- Orphaned SMC Document File: " << local_path << " - deleting...";

                try {
                    QFile::remove(local_path);
                } catch (...) {
                    qDebug() << "----- ERROR removing file: " << local_path;
                }
            }
        }
    }

    ret = true;

    return ret;
}

bool EX_Canvas::reloadCourseList()
{
    // Clear and reload the course list
    _course_list.clear();

    if (_app_db == nullptr) {
        qDebug() << "ERROR - No valid _app_db";
        return false;
    }

    QSqlRecord record;
    GenericTableModel *model = nullptr;

    // Get the courses table
    model = _app_db->getTable("courses");
    if (model == nullptr) {
        // Unable to pull the courses table, error with database?
        QString err = "ERROR - pulling courses table!!!";
        qDebug() << err;
        return false;
    }

    model->setFilter("");
    model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(model->canFetchMore()) { model->fetchMore(); }

    int rowCount = model->rowCount();
    for (int i=0; i < rowCount; i++) {
        record = model->record(i);
        QString course_id = record.value("id").toString();
        QString course_name = record.value("name").toString();
        _course_list[course_id] = course_name;
        qDebug() << "ADDED COURSE TO LIST " << course_id << course_name;
    }

    return true;
}

bool EX_Canvas::reloadAssignmentList()
{
    // Clear and reload the assignment list
    _assignment_list.clear();

    if (_app_db == nullptr) {
        qDebug() << "ERROR - No valid _app_db";
        return false;
    }

    QSqlRecord record;
    GenericTableModel *model = nullptr;

    // Get the courses table
    model = _app_db->getTable("assignments");
    if (model == nullptr) {
        // Unable to pull the courses table, error with database?
        QString err = "ERROR - pulling assignments table!!!";
        qDebug() << err;
        return false;
    }

    model->setFilter("");
    model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(model->canFetchMore()) { model->fetchMore(); }

    int rowCount = model->rowCount();
    for (int i=0; i < rowCount; i++) {
        record = model->record(i);
        QString assignment_id = record.value("id").toString();
        QString assignment_name = record.value("name").toString();
        _assignment_list[assignment_id] = assignment_name;
        qDebug() << "ADDED ASSIGNMENT TO LIST " << assignment_id << assignment_name;
    }

    return true;
}

bool EX_Canvas::setCurrentItem(QString item_text)
{
    progressCurrentItem = item_text;

    return true;
}

QString EX_Canvas::appDataFolder()
{
    // Cast appmodule back to its class
    AppModule *app_module = qobject_cast<AppModule*>(this->parent());

    return app_module->appDataFolder();
}

QSqlRecord EX_Canvas::pullSinglePage(QString course_id, QString page_url)
{
    QSqlTableModel *pages_model = _app_db->getTable("pages");
    if (pages_model == nullptr) {
        qDebug() << "Error getting model for Pages in pullSinglePage " << page_url;
        return QSqlRecord();
    }
    // Pull the page from Canvas and update the database with current info

    QString page_body = "";
    QString page_id = "";

    // Need to retrieve each page body individually
    QHash<QString,QString> p;
    p["per_page"] = "10000"; // Cuts down number of calls significantly
    QJsonDocument page_doc = CanvasAPICall("/api/v1/courses/" + course_id + "/pages/" + page_url, "GET", &p);
    QJsonObject page_object;
    if (!page_doc.isObject()) {
        qDebug() << "!!!ERROR GETTING PAGE BODY - course:" << course_id << page_url << page_doc;
        page_body = "ERROR GETTING PAGE";
        return QSqlRecord();
    } else {
        page_object = page_doc.object();
        page_body = page_object["body"].toString("");
        if (page_object["locked_for_user"].toBool() == true) {
            page_body = page_object["lock_explanation"].toString("Page Locked - see instructor");
        }
    }

    page_id = page_doc["page_id"].toString("");
    if (page_id == "") {
        qDebug() << "** ERROR Getting Page Info for " << page_url;
        return QSqlRecord();
    }

    // Convert SMC Video/Document/Etc links to local links
    page_body = ProcessAllLinks(page_body);

    pages_model->setFilter("url='" + page_url.replace("'", "''") + "' AND course_id='" + course_id.replace("'", "''") + "'");
    pages_model->select();
    // NOTE - Make sure to fetch all or we may only get 256 records
    while(pages_model->canFetchMore()) { pages_model->fetchMore(); }

    QSqlRecord record;
    bool is_insert = false;

    if (pages_model->rowCount() >= 1) {
        // Row exists, update with current info
        record = pages_model->record(0);
        is_insert = false;
        qDebug() << "\t\t\tUpdating page..." << page_url;
    } else {
        // Need to clear the filter to insert
        pages_model->setFilter("");
        record = pages_model->record();
        is_insert = true;
        qDebug() << "\t\t\tImporting page info..." << page_url;
    }

    // JSON - list of objects
    // {"title":"Format of the course","created_at":"2017-06-21T21:44:15Z",
    // "url":"format-of-the-course","editing_roles":"teachers",
    // "page_id":26664700000000089,"published":true,"hide_from_students":false,
    // "front_page":false,
    // "html_url":"https://canvas.ed.dev/courses/26664700000000090/pages/format-of-the-course",
    // "updated_at":"2017-06-21T21:44:15Z","locked_for_user":false}

    record.setValue("title", page_object["title"].toString(""));
    record.setValue("created_at", page_object["created_at"].toString(""));
    record.setValue("url", page_object["url"].toString(""));
    record.setValue("editing_roles", page_object["editing_roles"].toString(""));
    record.setValue("page_id", page_object["page_id"].toString(""));
    record.setValue("published", page_object["published"].toBool(false));
    record.setValue("hide_from_students", page_object["hide_from_students"].toBool(false));
    record.setValue("front_page", page_object["front_page"].toBool(false));
    record.setValue("html_url", page_object["html_url"].toString(""));
    record.setValue("updated_at", page_object["updated_at"].toString(""));
    record.setValue("locked_for_user", page_object["locked_for_user"].toBool(false));
    record.setValue("course_id", course_id);
    record.setValue("body", page_body);
    record.setValue("lock_info", page_object["lock_info"].toString(""));
    record.setValue("lock_explanation", page_object["lock_explanation"].toString(""));
    record.setValue("is_active", "true");

    if (is_insert) {
       pages_model->insertRecord(-1, record);
    } else {
       // Filter should be set so 0 should be current record
       pages_model->setRecord(0, record);
    }
    // Write changes
    if (!pages_model->submitAll()) {
        qDebug() << "Error saving page info " << pages_model->lastError();
    }

    pages_model->setFilter(""); // clear the filter
    pages_model->select();

    //qDebug() << "Page " << o["title"].toString("");
    pages_model->database().commit();
    //qDebug() << model->lastError();

    return record;
}



/*
 *
 *
 * private static string ConvertDictionaryToQueryString(Dictionary<string, object> p)
        {
            if (p == nullptr) { return ""; }

            StringBuilder ret = new StringBuilder();

            bool first = true;

            foreach (string key in p.Keys)
            {
                if (key == nullptr) { continue; }

                if (p[key] == nullptr) { p[key] = ""; }

                // Put in the & between values
                if (!first) { ret.Append("&"); }
                ret.Append(HttpUtility.UrlEncode(key));
                ret.Append("=");
                ret.Append(HttpUtility.UrlEncode(p[key].ToString()));
                first = false;
            }

            return ret.ToString();
        }

        private static Dictionary<string,object> CanvasAPICall(string api_call, string method = "GET", Dictionary<string,object> p = nullptr)
        {
            string response_json = "";
            Dictionary<string, object> response_items;

            // Don't error out on test certs
            ServicePointManager.ServerCertificateValidationCallback = delegate { return true; };

            WebRequest wr = nullptr;

            string qstring = "";

            if (p != nullptr && p.Count > 0 && method.ToUpper() == "GET")
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
            if (p != nullptr && p.Count > 0 && (method.ToUpper() == "POST" || method.ToUpper() == "PUT"))
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

            WebResponse response = nullptr;
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

            if (response_items == nullptr)
            {
                // Don't return a nullptr, return an empty dictionary
                response_items = new Dictionary<string,object>();
            }

            return response_items;
        }


        */


