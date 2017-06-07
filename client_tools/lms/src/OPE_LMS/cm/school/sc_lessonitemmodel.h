#ifndef SC_LESSONITEMMODEL_H
#define SC_LESSONITEMMODEL_H

#include <QObject>
#include <QList>
#include <QAbstractListModel>

#include "../cm_persistentobjectmodel.h"
#include "sc_lessonitem.h"

class SC_LessonItemModel : public CM_PersistentObjectModel
{
    Q_OBJECT
public:
    explicit SC_LessonItemModel(QObject *parent = 0);

    virtual CM_PersistentObject* createItemObject(QObject *parent = 0)
    {
        //qDebug() << "SC_LessonItem - CreateItemObject";
        SC_LessonItem *p = new SC_LessonItem(parent);
        return p;
    }

signals:

public slots:

};

#endif // SC_LESSONITEMMODEL_H
