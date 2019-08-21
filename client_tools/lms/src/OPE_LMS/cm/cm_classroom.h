#ifndef CM_CLASSROOM_H
#define CM_CLASSROOM_H

#include <QObject>
#include <QSqlDatabase>
//#include <QMessageBox>
#include <QSqlQuery>
#include <QVariant>

#include "cm_sequentialguid.h"

class CM_Classroom : public QObject
{
    Q_OBJECT
public:
    explicit CM_Classroom(QObject *parent = nullptr);
    
    void InitDB();

    QSqlQuery *GetClassroomList();
    void AddClassroom(QString room_name);
signals:

public slots:

private:
    QString con_string;
    bool db_init;
    bool db_connected;


};


#endif // CM_CLASSROOM_H
