#include "cm_database.h"

bool CM_Database::_isDBConnected = false;
QSqlDatabase CM_Database::db;


CM_Database::CM_Database(QObject *parent) :
    QObject(parent)
{

}


bool CM_Database::DBConnect() {
    bool ret = false;

    if (!_isDBConnected)
    {
        db = QSqlDatabase::addDatabase("QSQLITE");
        db.setDatabaseName("cm_database");
        //db.setHostName("acidalia");
        //db.setUserName("mojito");
        //db.setPassword("J0a1m8");
        bool ok = db.open();
        ret = ok;
    } else {
        ret = true;
    }

    return ret;
}


QSqlQuery *CM_Database::Query(QString sql)
{
    if (!DBConnect()) { return NULL; }

    QSqlQuery *ret = new QSqlQuery();
    ret->exec(sql);

    return ret;
}
