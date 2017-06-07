#ifndef SC_PROGRAMS_H
#define SC_PROGRAMS_H

#include <QObject>
#include <QList>

#include "cm/cm_persistentobject.h"

class SC_Programs : public CM_PersistentObject
{
    Q_OBJECT
public:
    explicit SC_Programs(QObject *parent = 0);

    virtual CM_PersistentObject* createItemObject(QObject *parent = 0)
    {
        //qDebug() << "SC_Programs - createItemObject";
        SC_Programs *p = new SC_Programs(parent);
        return p;
    }

    Q_PROPERTY(QString name READ name WRITE setName NOTIFY nameChanged)
    Q_PROPERTY(QString instructor READ instructor WRITE setInstructor NOTIFY instructorChanged)
signals:
    void nameChanged(QString);
    void instructorChanged(QString);

public slots:

    QString name() { return _VALUES["name"]; }
    void setName(QString name) { SetValue("name", name); }

    QString instructor() { return _VALUES["instructor"]; }
    void setInstructor(QString instructor) { SetValue("instructor", instructor); }

private:

};

#endif // SC_PROGRAMS_H
