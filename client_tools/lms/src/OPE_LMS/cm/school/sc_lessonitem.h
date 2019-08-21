#ifndef SC_LESSONITEM_H
#define SC_LESSONITEM_H

#include <QObject>
#include <QList>

#include "cm/cm_persistentobject.h"

class SC_LessonItem : public CM_PersistentObject
{
    Q_OBJECT
public:
    explicit SC_LessonItem(QObject *parent = nullptr);

    virtual CM_PersistentObject* createItemObject(QObject *parent = nullptr)
    {
        //qDebug() << "SC_LessonItem - createItemObject";
        SC_LessonItem *p = new SC_LessonItem(parent);
        return p;
    }

    Q_PROPERTY(QString name READ name WRITE setName NOTIFY nameChanged)

signals:
    void nameChanged(QString);

public slots:

    QString name() { return _VALUES["name"]; }
    void setName(QString name) { SetValue("name", name); }

private:

};

#endif // SC_LESSONITEM_H
