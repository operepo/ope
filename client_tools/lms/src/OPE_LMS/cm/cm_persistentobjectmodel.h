#ifndef CM_PERSISTENTOBJECTMODEL_H
#define CM_PERSISTENTOBJECTMODEL_H

#include <QObject>
#include <QList>
#include <QAbstractListModel>

#include "cm_persistentobject.h"

class CM_PersistentObjectModel : public QAbstractListModel
{
    Q_OBJECT
public:
    explicit CM_PersistentObjectModel(QObject *parent = nullptr);

    // Redefine this to create the item object
    virtual CM_PersistentObject* createItemObject(QObject *parent = nullptr)
    {
        //qDebug() << "CM_PersistentObjectModel - CreateItemObject";
        CM_PersistentObject *p = new CM_PersistentObject(parent);
        return p;
    }

    Q_PROPERTY(QString parentItem READ parentItem WRITE setParentItem NOTIFY parentItemChanged)
    void loadItemList(QString parent_item = "");

    void generateRoleNames();
    QHash<int, QByteArray> roleNames() const;

    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const;
    Qt::ItemFlags flags(const QModelIndex & index) const ;
    int rowCount(const QModelIndex &parent = QModelIndex()) const;

    Q_PROPERTY(int count READ count NOTIFY countChanged)
    int count() const;

signals:
    void countChanged();

    void parentItemChanged(QString parent_item);
public slots:
    QString parentItem() { return _parent_item; }
    void setParentItem(QString parent_item) { _parent_item = parent_item; loadItemList(); emit parentItemChanged(_parent_item); }

    void insert(int index, const QString &name);
    void append(const QString &name);
    void remove(int index);
    QObject *get(int index);
    void setProperty(int index, const QString & property, const QVariant &value);
    bool setData(const QModelIndex & index, const QVariant & value, int role = Qt::EditRole);

private:
    QList<CM_PersistentObject *> item_list;

    // Used to store the roles list after it is generated
    QHash<int, QByteArray> role_list;
    QString _parent_item;

};

#endif // CM_PERSISTENTOBJECTMODEL_H
