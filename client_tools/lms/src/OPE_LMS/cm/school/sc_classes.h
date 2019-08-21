#ifndef SC_CLASSES_H
#define SC_CLASSES_H

#include <QObject>
#include "../cm_persistentobject.h"

class SC_Classes : public CM_PersistentObject
{
    Q_OBJECT
public:
    explicit SC_Classes(QObject *parent=nullptr);

    virtual CM_PersistentObject* createItemObject(QObject *parent = nullptr)
    {
        //qDebug() << "SC_Classes - createItemObject";
        SC_Classes *p = new SC_Classes(parent);
        return p;
    }

    Q_PROPERTY(QString name READ name WRITE setName NOTIFY nameChanged)
    Q_PROPERTY(QString number READ number WRITE setNumber NOTIFY numberChanged)
    Q_PROPERTY(QString instructor READ instructor WRITE setInstructor NOTIFY instructorChanged)

signals:
    void nameChanged(QString);
    void numberChanged(QString);
    void instructorChanged(QString);

public slots:
    QString name() { return _VALUES["name"]; }
    void setName(QString name) { SetValue("name", name); }

    QString number() { return _VALUES["number"]; }
    void setNumber(QString number) { SetValue("number", number); }

    QString instructor() { return _VALUES["instructor"]; }
    void setInstructor(QString instructor) { SetValue("instructor", instructor); }


};

#endif // SC_CLASSES_H
