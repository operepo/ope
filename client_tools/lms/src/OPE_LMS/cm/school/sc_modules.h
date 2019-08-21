#ifndef SC_MODULES_H
#define SC_MODULES_H

#include <QObject>
#include <QList>

#include "cm/cm_persistentobject.h"

class SC_Modules : public CM_PersistentObject
{
    Q_OBJECT
public:
    explicit SC_Modules(QObject *parent = nullptr);

    virtual CM_PersistentObject* createItemObject(QObject *parent = nullptr)
    {
        //qDebug() << "SC_Programs - createItemObject";
        SC_Modules *p = new SC_Modules(parent);
        return p;
    }

    Q_PROPERTY(QString name READ name WRITE setName NOTIFY nameChanged)
    Q_PROPERTY(QString shortDescription READ shortDescription WRITE setShortDescription NOTIFY shortDescriptionChanged)
    Q_PROPERTY(QString description READ description WRITE setDescription NOTIFY descriptionChanged)
signals:
    void nameChanged(QString);
    void shortDescriptionChanged(QString);
    void descriptionChanged(QString);

public slots:

    QString name() { return _VALUES["name"]; }
    void setName(QString name) { SetValue("name", name); }

    QString shortDescription() { return _VALUES["short_description"]; }
    void setShortDescription(QString short_description) { SetValue("short_description", short_description); }

    QString description() { return _VALUES["description"]; }
    void setDescription(QString description) { SetValue("description", description); }

private:

};

#endif // SC_MODULES_H
