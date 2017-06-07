#include "db.h"

APP_DB::APP_DB(QQmlApplicationEngine *parent) : QObject(parent)
{
    _db = QSqlDatabase::addDatabase("QSQLITE");
    this->setParent(parent);

    // DEBUG STUFF
    QString crypt_pw = QCryptographicHash::hash(QString("abcd").toLocal8Bit(),
            QCryptographicHash::Sha256).toBase64(QByteArray::Base64UrlEncoding | QByteArray::OmitTrailingEquals);
    qDebug() << "TEST PW: " << crypt_pw;
}

/**
 * @brief DB::init_db - Connect to database and ensure that scheme is in place and/or migrated
 * @return true on success
 */
bool APP_DB::init_db()
{
    bool ret = false;

    QQmlApplicationEngine *p = qobject_cast<QQmlApplicationEngine*>(this->parent());

    p->rootContext()->setContextProperty("database", this);

    // Find DB path
    QDir d;
    d.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/");
    d.mkpath(d.path());
    QString db_file = d.path() + "/lms.db";

    _db.setHostName(db_file);
    _db.setDatabaseName(db_file);
    _db.setPassword("TEST PW"); // TODO - doesn't do anything, need sqlite extetion to add encryption?

    ret = _db.open();

    if (ret) {
        // Create and/or migrate tables
        QSqlQuery query;
        QString sql;
        //QSqlTableModel *model;
        GenericQueryModel *model;

        // Create student users table
        sql = "CREATE TABLE IF NOT EXISTS `students` ( \
                `id`	INTEGER PRIMARY KEY AUTOINCREMENT, \
                `user_name`	TEXT NOT NULL, \
                `password`	TEXT NOT NULL, \
                `auth_cookie`	TEXT NOT NULL DEFAULT '' \
            );";

        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericQueryModel(this);
        //model->setTable("students");
        //model->setEditStrategy(QSqlTableModel::OnManualSubmit);
        //model->select();
        //model->setHeaderData(0, Qt::Horizontal, tr("id"));
        //model->setHeaderData(1, Qt::Horizontal, tr("user_name"));
        //model->setHeaderData(2, Qt::Horizontal, tr("password"));
        //model->setHeaderData(3, Qt::Horizontal, tr("auth_cookie"));
        _tables["students"] = model;

        // Expose this to QML
        p->rootContext()->setContextProperty("students_model", model);


        // Create the classes table
        sql = "CREATE TABLE IF NOT EXISTS `classes` ( \
                `id`	INTEGER PRIMARY KEY AUTOINCREMENT, \
                `tid_student`	INTEGER NOT NULL DEFAULT 0, \
                `class_name`	TEXT NOT NULL DEFAULT '', \
                `class_code`	TEXT NOT NULL DEFAULT '', \
                `class_description`	TEXT NOT NULL DEFAULT '' \
            );";
        if (!query.exec(sql)) {
            qDebug() << "DB Error: " << query.lastError().text();
            ret = false;
        }
        // Add to the table models list
        model = new GenericQueryModel(this);
        //model->select();
        //model->setHeaderData(0, Qt::Horizontal, tr("id"));
        //model->setHeaderData(1, Qt::Horizontal, tr("tid_student"));
        //model->setHeaderData(2, Qt::Horizontal, tr("class_name"));
        //model->setHeaderData(3, Qt::Horizontal, tr("class_code"));
        //model->setHeaderData(4, Qt::Horizontal, tr("class_description"));
        _tables["classes"] = model;

        // Expose this to QML
        p->rootContext()->setContextProperty("classes_model", model);


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
        model = new GenericQueryModel(this);
        model->setQuery("SELECT * FROM resources", _db);
        //model->select();
        //model->setHeaderData(0, Qt::Horizontal, tr("id"));
        //model->setHeaderData(1, Qt::Horizontal, tr("resource_name"));
        //model->setHeaderData(2, Qt::Horizontal, tr("resource_url"));
        //model->setHeaderData(3, Qt::Horizontal, tr("resource_description"));
        //model->setHeaderData(4, Qt::Horizontal, tr("sort_order"));
        _tables["resources"] = model;

        // Expose this to QML
        p->rootContext()->setContextProperty("resources_model", model);

        // Make sure the default resource entries are in place
        add_resource("Start Here", "/start_here/index.html", "Getting started...", 0);


        // Make sure to commit and release locks
        _db.commit();

    }

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

GenericQueryModel::GenericQueryModel(QObject *parent) : QSqlQueryModel(parent)
{

}

void GenericQueryModel::setQuery(const QString &query, const QSqlDatabase &db)
{
    QSqlQueryModel::setQuery(query, db);
    generateRoleNames();

}

void GenericQueryModel::setQuery(const QSqlQuery &query)
{
    QSqlQueryModel::setQuery(query);
    generateRoleNames();
}

QVariant GenericQueryModel::data(const QModelIndex &index, int role) const
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

void GenericQueryModel::generateRoleNames()
{
    m_roleNames.clear();
    for(int i = 0; i < record().count(); i++) {
        m_roleNames.insert(Qt::UserRole + i + 1, record().fieldName(i).toUtf8());
    }
}

