#ifndef SC_PROGRAMMODEL_H
#define SC_PROGRAMMODEL_H

#include <QObject>
#include <QList>
#include <QAbstractListModel>

#include "../cm_persistentobjectmodel.h"
#include "sc_programs.h"

class SC_ProgramModel : public CM_PersistentObjectModel
{
    Q_OBJECT
public:

    explicit SC_ProgramModel(QObject *parent = nullptr);

    virtual CM_PersistentObject* createItemObject(QObject *parent = nullptr)
    {
        //qDebug() << "SC_ProgramModel - CreateItemObject";
        SC_Programs *p = new SC_Programs(parent);
        return p;
    }

};

#endif // SC_PROGRAMMODEL_H
