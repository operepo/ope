#include "db.h"

APP_DB::APP_DB(QQmlApplicationEngine *parent) : QObject(parent)
{
    _db = QSqlDatabase::addDatabase("QSQLITE");
    this->setParent(parent);

    // DEBUG STUFF
    //QString crypt_pw = QCryptographicHash::hash(QString("abcd").toLocal8Bit(),
    //        QCryptographicHash::Sha256).toBase64(QByteArray::Base64UrlEncoding | QByteArray::OmitTrailingEquals);
    //qDebug() << "TEST PW: " << crypt_pw;

    QQmlApplicationEngine *p = qobject_cast<QQmlApplicationEngine*>(this->parent());
    if (p == NULL) {
        // Unable to get app engine
        qDebug() << "FATAL ERROR - APP_DB Unable to get the QML Application Engine.";
        QCoreApplication::quit();
        return;
    }

    //p->rootContext()->setContextProperty("database", this);
}

/**
 * @brief DB::init_db - Connect to database and ensure that scheme is in place and/or migrated
 * @return true on success
 */
bool APP_DB::init_db()
{
    bool ret = false;

    // Find DB path
    QDir d;
    d.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/");
    d.mkpath(d.path());
    QString db_file = d.path() + "/lms.db";

    _db.setHostName(db_file);
    _db.setDatabaseName(db_file);
    //_db.setPassword("TEST PW"); // TODO - doesn't do anything, need sqlite extetion to add encryption?

    ret = _db.open();

    QSqlQuery query;
    QString sql;
    //QSqlTableModel *model;
    GenericTableModel *model;

    if (ret) {
        // Create and/or migrate tables

        // ===========================================
        // Create student users table
        sql = "CREATE TABLE IF NOT EXISTS `users` ( \
                `id`            TEXT NOT NULL DEFAULT '', \
                `name`          TEXT NOT NULL DEFAULT '', \
                `sortable_name` TEXT NOT NULL DEFAULT '', \
                `short_name`    TEXT NOT NULL DEFAULT '', \
                `permissions`   TEXT NOT NULL DEFAULT '' \
                );";

        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "users", _db);

        // ===========================================
        // Create the courses table
        sql = "CREATE TABLE IF NOT EXISTS `courses` ( \
                `id`            TEXT NOT NULL DEFAULT '', \
                `name`          TEXT NOT NULL DEFAULT '', \
                `account_id`    TEXT NOT NULL DEFAULT '', \
                `start_at`      TEXT NOT NULL DEFAULT '', \
                `grading_standard_id` TEXT NOT NULL DEFAULT '', \
                `is_public`     TEXT NOT NULL DEFAULT '', \
                `course_code`   TEXT NOT NULL DEFAULT '', \
                `default_view`  TEXT NOT NULL DEFAULT '', \
                `root_account_id` TEXT NOT NULL DEFAULT '', \
                `enrollment_term_id` TEXT NOT NULL DEFAULT '', \
                `end_at`        TEXT NOT NULL DEFAULT '', \
                `public_syllabus` TEXT NOT NULL DEFAULT '', \
                `public_syllabus_to_auth` TEXT NOT NULL DEFAULT '', \
                `storage_quota_mb` TEXT NOT NULL DEFAULT '', \
                `is_public_to_auth_users` TEXT NOT NULL DEFAULT '', \
                `apply_assignment_group_weights` TEXT NOT NULL DEFAULT '', \
                `calendar`       TEXT NOT NULL DEFAULT '', \
                `time_zone`      TEXT NOT NULL DEFAULT '', \
                `hide_final_grades` TEXT NOT NULL DEFAULT '', \
                `workflow_state` TEXT NOT NULL DEFAULT '', \
                `restrict_enrollments_to_course_dates` TEXT NOT NULL DEFAULT '', \
                `enrollment_type` TEXT NOT NULL DEFAULT '', \
                `enrollment_role` TEXT NOT NULL DEFAULT '', \
                `enrollment_role_id` TEXT NOT NULL DEFAULT '', \
                `enrollment_state` TEXT NOT NULL DEFAULT '', \
                `enrollment_user_id` TEXT NOT NULL DEFAULT '' \
                );";
        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "courses", _db);


        // ===========================================
        // Create modules  table
        sql = "CREATE TABLE IF NOT EXISTS `modules` ( \
                `id`            TEXT NOT NULL DEFAULT '', \
                `name`          TEXT NOT NULL DEFAULT '', \
                `position`      TEXT NOT NULL DEFAULT '', \
                `unlock_at`     TEXT NOT NULL DEFAULT '' , \
                `require_sequential_progress` TEXT NOT NULL DEFAULT '', \
                `publish_final_grade` TEXT NOT NULL DEFAULT '', \
                `prerequisite_module_ids` TEXT NOT NULL DEFAULT '', \
                `published`     TEXT NOT NULL DEFAULT '', \
                `items_count`   TEXT NOT NULL DEFAULT '', \
                `items_url`     TEXT NOT NULL DEFAULT '', \
                `course_id`     TEXT NOT NULL DEFAULT '' \
                );";

        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "modules", _db);


        // ===========================================
        // Create module_items table
        sql = "CREATE TABLE IF NOT EXISTS `module_items` ( \
                `id`            TEXT NOT NULL DEFAULT '', \
                `title`          TEXT NOT NULL DEFAULT '', \
                `position`      TEXT NOT NULL DEFAULT '', \
                `indent`     TEXT NOT NULL DEFAULT '' , \
                `type` TEXT NOT NULL DEFAULT '', \
                `module_id` TEXT NOT NULL DEFAULT '', \
                `html_url` TEXT NOT NULL DEFAULT '', \
                `page_url`     TEXT NOT NULL DEFAULT '', \
                `url`   TEXT NOT NULL DEFAULT '', \
                `published`     TEXT NOT NULL DEFAULT '' \
                );";

        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "module_items", _db);


        // ===========================================
        // Create files table - holds file info
        sql = "CREATE TABLE IF NOT EXISTS `files` ( \
                `id`            TEXT NOT NULL DEFAULT '', \
                `folder_id`     TEXT NOT NULL DEFAULT '', \
                `display_name`  TEXT NOT NULL DEFAULT '', \
                `filename`      TEXT NOT NULL DEFAULT '', \
                `content_type`  TEXT NOT NULL DEFAULT '', \
                `url`           TEXT NOT NULL DEFAULT '', \
                `size`          TEXT NOT NULL DEFAULT '', \
                `created_at`    TEXT NOT NULL DEFAULT '', \
                `updated_at`    TEXT NOT NULL DEFAULT '', \
                `unlock_at`     TEXT NOT NULL DEFAULT '', \
                `locked`        TEXT NOT NULL DEFAULT '', \
                `hidden`        TEXT NOT NULL DEFAULT '', \
                `lock_at`       TEXT NOT NULL DEFAULT '', \
                `hidden_for_user` TEXT NOT NULL DEFAULT '', \
                `thumbnail_url` TEXT NOT NULL DEFAULT '', \
                `modified_at`   TEXT NOT NULL DEFAULT '', \
                `mime_class`    TEXT NOT NULL DEFAULT '', \
                `media_entry_id` TEXT NOT NULL DEFAULT '', \
                `locked_for_user` TEXT NOT NULL DEFAULT '', \
                `course_id`     TEXT NOT NULL DEFAULT '', \
                `pull_file`      TEXT NOT NULL DEFAULT '', \
                `local_copy_present`    TEXT NOT NULL DEFAULT '' \
                );";

        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "files", _db);



        // ===========================================
        // Create pages table
        sql = "CREATE TABLE IF NOT EXISTS `pages` ( \
                `title`         TEXT NOT NULL DEFAULT '', \
                `created_at`    TEXT NOT NULL DEFAULT '', \
                `url`           TEXT NOT NULL DEFAULT '', \
                `editing_roles` TEXT NOT NULL DEFAULT '', \
                `page_id`       TEXT NOT NULL DEFAULT '', \
                `published`     TEXT NOT NULL DEFAULT '', \
                `hide_from_students` TEXT NOT NULL DEFAULT '', \
                `front_page`    TEXT NOT NULL DEFAULT '', \
                `html_url`      TEXT NOT NULL DEFAULT '', \
                `updated_at`    TEXT NOT NULL DEFAULT '', \
                `locked_for_user` TEXT NOT NULL DEFAULT '', \
                `body`          TEXT NOT NULL DEFAULT '', \
                `lock_info`     TEXT NOT NULL DEFAULT '', \
                `lock_explanation` TEXT NOT NULL DEFAULT '', \
                `course_id`     TEXT NOT NULL DEFAULT '' \
                );";

        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "pages", _db);



        // ===========================================
        // Create conversations table - messaging
        sql = "CREATE TABLE IF NOT EXISTS `conversations` ( \
                `id`            TEXT NOT NULL DEFAULT '', \
                `subject`       TEXT NOT NULL DEFAULT '', \
                `workflow_state` TEXT NOT NULL DEFAULT '', \
                `last_message`  TEXT NOT NULL DEFAULT '', \
                `last_message_at` TEXT NOT NULL DEFAULT '', \
                `last_authored_message` TEXT NOT NULL DEFAULT '', \
                `last_authored_message_at` TEXT NOT NULL DEFAULT '', \
                `message_count` TEXT NOT NULL DEFAULT '', \
                `subscribed`    TEXT NOT NULL DEFAULT '', \
                `private`       TEXT NOT NULL DEFAULT '', \
                `starred`       TEXT NOT NULL DEFAULT '', \
                `properties`    TEXT NOT NULL DEFAULT '', \
                `audience`      TEXT NOT NULL DEFAULT '', \
                `audience_contexts` TEXT NOT NULL DEFAULT '', \
                `avatar_url`    TEXT NOT NULL DEFAULT '', \
                `participants`  TEXT NOT NULL DEFAULT '', \
                `visible`       TEXT NOT NULL DEFAULT '', \
                `context_code`  TEXT NOT NULL DEFAULT '', \
                `context_name`  TEXT NOT NULL DEFAULT '', \
                `submissions`   TEXT NOT NULL DEFAULT '' \
                );";

        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "conversations", _db);


        // ===========================================
        // Create messages table
        sql = "CREATE TABLE IF NOT EXISTS `messages` ( \
                `id`            TEXT NOT NULL DEFAULT '', \
                `author_id`     TEXT NOT NULL DEFAULT '', \
                `created_at`    TEXT NOT NULL DEFAULT '', \
                `generated`     TEXT NOT NULL DEFAULT '', \
                `body`          TEXT NOT NULL DEFAULT '', \
                `forwarded_messages` TEXT NOT NULL DEFAULT '', \
                `attachments`   TEXT NOT NULL DEFAULT '', \
                `media_comment` TEXT NOT NULL DEFAULT '', \
                `participating_user_ids` TEXT NOT NULL DEFAULT '', \
                `conversation_id` TEXT NOT NULL DEFAULT '', \
                `scope`         TEXT NOT NULL DEFAULT '' \
                );";

        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "messages", _db);




        // Create the resources table
        sql = "CREATE TABLE IF NOT EXISTS `resources` ( \
                `id`	INTEGER PRIMARY KEY AUTOINCREMENT, \
                `resource_name`	TEXT NOT NULL DEFAULT '', \
                `resource_url`	TEXT NOT NULL DEFAULT '', \
                `resource_description`	TEXT NOT NULL DEFAULT '', \
                `sort_order`	INTEGER NOT NULL DEFAULT 0 \
            );";
        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericTableModel(this, "resources", _db);

        // Make sure the default resource entries are in place
        add_resource("Start Here", "/start_here/index.html", "Getting started...", 0);


        // Make sure to commit and release locks
        _db.commit();

    }

    //qDebug() << "DB INIT complete " << this;
    return ret;
}

/**
 * @brief APP_DB::auth_student - Authenticate the student against the local database
 * @param user_name
 * @param password
 * @return true on success
 */
bool APP_DB::auth_student(QString user_name, QString password)
{
    bool ret = false;

    // If the password is empty always return false
    if (password == "") {
        return false;
    }

    // Encode password
    QString crypt_pw = QCryptographicHash::hash(password.toLocal8Bit(),
            QCryptographicHash::Sha256).toBase64(QByteArray::Base64UrlEncoding | QByteArray::OmitTrailingEquals);

    // Query to see if the user exists
    QString sql = "SELECT COUNT(*) user_count FROM students WHERE user_name=:user_name and password=:password";
    QSqlQuery q;
    q.prepare(sql);
    q.bindValue(":user_name", user_name);
    q.bindValue(":password", crypt_pw);
    q.exec();
    int user_count = 0;
    while(q.next()) {
        user_count = q.value("user_count").toInt();
    }

    if (user_count > 0) {
        ret = true;
    }

    return ret;
}

bool APP_DB::add_resource(QString resource_name, QString resource_url, QString resource_description, int sort_order)
{
    bool ret = false;
    QString sql;
    QSqlQuery q;

    // Check if the resource exists
    sql = "SELECT count(*) as count FROM resources WHERE resource_name=:resource_name";
    q.prepare(sql);
    q.bindValue(":resource_name", resource_name);
    q.exec();
    int count = 0;
    while (q.next()) {
        count = q.value("count").toInt();
    }

    if (count > 0) {
        // Already present
        return true;
    }

    // Not present, add it
    sql = "INSERT INTO resources (resource_name, resource_url, resource_description, sort_order) \
        VALUES (:resource_name, :resource_url, :resource_description, :sort_order)";


    q.prepare(sql);
    q.bindValue(":resource_name", resource_name);
    q.bindValue(":resource_url", resource_url);
    q.bindValue(":resource_description", resource_description);
    q.bindValue(":sort_order", sort_order);
    q.exec();

    // Write changes to the db
    _db.commit();

    // Refresh data after insert? TODO - should this be an emit signal instead?
    //_tables["resources"]->select();

    ret = true;

    return ret;
}

GenericTableModel *APP_DB::getTable(QString table_name)
{
    //qDebug() << "getTable " << this;
    if (_tables.isEmpty())
        return NULL;

    if (_tables.contains(table_name)) {
        return _tables[table_name];
    }

    return NULL;
}

GenericTableModel::GenericTableModel(APP_DB *parent, QString table_name, QSqlDatabase db) : QSqlTableModel(parent, db)
{
    setTable(table_name);
    setEditStrategy(QSqlTableModel::OnManualSubmit);
    select();
    if (parent != NULL) {
        parent->_tables[table_name] = this;

        // Expose this to QML
        QQmlEngine *p = qobject_cast<QQmlApplicationEngine*>(this->parent()->parent());
        if (p == NULL) {
            // Unable to get app engine
            qDebug() << "FATAL ERROR - Generic Table Model Unable to get the QML Application Engine.";
            QCoreApplication::quit();
            return;
        }
        //p->rootContext()->setContextProperty(table_name + "_model", this);
    }
}

void GenericTableModel::setTable(QString tableName)
{
    QSqlTableModel::setTable(tableName);
    generateRoleNames();
}

QVariant GenericTableModel::data(const QModelIndex &index, int role) const
{
    QVariant value;

    if (role < Qt::UserRole) {
        value = QSqlQueryModel::data(index, role);
    } else {
        int columnIndex = role - Qt::UserRole -1;
        QModelIndex modelIndex = this->index(index.row(), columnIndex);
        value = QSqlQueryModel::data(modelIndex, Qt::DisplayRole);
    }

    return value;
}

void GenericTableModel::generateRoleNames()
{
    m_roleNames.clear();
    for(int i = 0; i < record().count(); i++) {
        m_roleNames.insert(Qt::UserRole + i + 1, record().fieldName(i).toUtf8());
    }
}

