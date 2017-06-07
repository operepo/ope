#ifndef CM_FILEINFO_H
#define CM_FILEINFO_H

#include <QObject>
#include <QList>
#include <QHash>
#include <QtSql>


#include "cm/cm_persistentobject.h"

class CM_FileInfo : public CM_PersistentObject
{
    Q_OBJECT
public:
    explicit CM_FileInfo();

    QString GetFileName();
    bool SetFileName(QString file_name);



signals:

public slots:

private:


};

#endif // CM_FILEINFO_H
