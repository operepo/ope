#ifndef SC_MODULEMODEL_H
#define SC_MODULEMODEL_H

#include <QObject>
#include <QList>
#include <QAbstractListModel>

#include "../cm_persistentobjectmodel.h"
#include "sc_modules.h"

class SC_ModuleModel : public CM_PersistentObjectModel
{
    Q_OBJECT
public:
    explicit SC_ModuleModel(QObject *parent = 0);

    virtual CM_PersistentObject* createItemObject(QObject *parent = 0)
    {
        //qDebug() << "SC_ProgramModel - CreateItemObject";
        SC_Modules *p = new SC_Modules(parent);
        return p;
    }
signals:

public slots:

};

#endif // SC_MODULEMODEL_H
