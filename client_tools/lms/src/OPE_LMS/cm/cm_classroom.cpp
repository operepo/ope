#include "cm_classroom.h"

CM_Classroom::CM_Classroom(QObject *parent) :
    QObject(parent)
{
    // Init class variables
    //con_string = ":memory:"; // Use this if you want it to forget your database when the app closes
    con_string = "sysmange.db";
    db_init = false;
    db_connected = false;


    InitDB();
}

QSqlQuery *CM_Classroom::GetClassroomList() {
    // Lookup the classroom list and return it
    QString sql = "SELECT guid, ClassroomName FROM `classrooms` ORDER BY ClassroomName";
    QSqlQuery *query = new QSqlQuery(sql);

    query->exec();
    return query;
}

void CM_Classroom::AddClassroom(QString room_name)
{
    // Insert into the classrooms table
    QString sql = "INSERT INTO `classrooms` (`guid`, `ClassroomName`) VALUES (:guid, :ClassroomName)";
    QSqlQuery query;
    query.prepare(sql);
    query.bindValue(":guid", CM_SequentialGUID::GetSequentialGUID(CM_SequentialGUID::SequentialAsString).toString());
    query.bindValue(":ClassroomName", QVariant(room_name));
    query.exec();

}

void CM_Classroom::InitDB() {
    QSqlDatabase db;
    if (!db_connected) {
        db = QSqlDatabase::addDatabase("QSQLITE");
        db.setDatabaseName(con_string);
        if(!db.open()) {
//            QMessageBox::critical(0, tr("Cannot open database"),
//                tr("Unable to establish a database connection.\n"
//                   "This example needs SQLite support. Please read "
//                   "the Qt SQL driver documentation for information how "
//                   "to build it."), QMessageBox::Cancel);
            return;
        }
        db_connected = true;
    }

    if (!db_init) {
        // Make sure that the tables and such exist
        QString sql = "CREATE TABLE IF NOT EXISTS `classrooms` (guid char(36) NOT NULL UNIQUE, ClassroomName char(300) ) ";

        QSqlQuery query;
        query.exec(sql);

        db_init = true;
    }


}
