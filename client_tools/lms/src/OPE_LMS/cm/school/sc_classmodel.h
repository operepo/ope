#ifndef SC_CLASSMODEL_H
#define SC_CLASSMODEL_H

#include <QObject>
#include <QList>
#include <QAbstractListModel>

#include "../cm_persistentobjectmodel.h"
#include "sc_classes.h"

class SC_ClassModel : public CM_PersistentObjectModel
{
    Q_OBJECT
public:

    explicit SC_ClassModel(QObject *parent = nullptr);

    virtual CM_PersistentObject* createItemObject(QObject *parent = nullptr)
    {
        //qDebug() << "SC_ClassModel - CreateItemObject";
        SC_Classes *p = new SC_Classes(parent);
        return p;
    }

};

#endif // SC_CLASSMODEL_H
