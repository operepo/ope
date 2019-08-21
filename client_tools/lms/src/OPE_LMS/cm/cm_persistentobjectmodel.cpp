#include "cm_persistentobjectmodel.h"

CM_PersistentObjectModel::CM_PersistentObjectModel(QObject *parent) :
    QAbstractListModel(parent)
{
    //qDebug() << "CM_PersistentObjectModel - Constructor";
}

void CM_PersistentObjectModel::loadItemList(QString parent_item)
{
    beginResetModel();

    if (parent_item != "")
    {
        setParentItem(parent_item);
    }

    // Load the items from the db
    CM_PersistentObject *p = createItemObject();
    QList<CM_PersistentObject *> pl = p->GetItemList(_parent_item);
    delete p;
    item_list.clear();
    for(int i=0; i<pl.count(); i++)
    {
        //qDebug() << "PersistentObject Item " << pl[i]->GetIDValue();
        item_list.append(pl[i]);
    }

    generateRoleNames();

    endResetModel();
}

void CM_PersistentObjectModel::generateRoleNames()
{
    //qDebug() << "Called role names...";

    if (role_list.count() > 0) { return; }

    // Load the keys from the first item
    QList<QString> keys;

    // Make sure these keys exist
    keys.append("name");
    keys.append("instructor");
    keys.append("description");

    if (item_list.count() > 0)
    {
        CM_PersistentObject *p = item_list[0];
        QList<QString> k = p->GetKeys();

        foreach (QString key, k)
        {
            if (!keys.contains(key)) { keys.append(key); }
        }
    }

    // Put use the keys as the roles
    for(int i = 0; i < keys.count(); i++)
    {
        //qDebug() << "Adding key (" << i << ") " << keys[i];
        QByteArray ar;
        ar.append(keys[i]);
        // We have to offset i with the UserRole value for
        // Qt to pick it up properly
        role_list[Qt::UserRole + i] = ar;
        //    roles[NameRole] = "name";
    }

    //qDebug() << "Roles Generated: " << role_list;
}

QHash<int, QByteArray> CM_PersistentObjectModel::roleNames() const
{
    return role_list;
}

int CM_PersistentObjectModel::rowCount(const QModelIndex &) const
{
    return item_list.count();
}

QVariant CM_PersistentObjectModel::data(const QModelIndex &index, int role) const
{
    //qDebug() << "ProgramModel::data" << index.row() << role;

    // validate index
    if (index.row() < 0 || index.row() >= item_list.count())
    {
        qDebug() << "invalid index leaving early...";
        return QVariant();
    }

    // Look for default roles
    // .... TODO Edit role, display role?
    if (role == Qt::DisplayRole || role == Qt::EditRole)
    {
        //// TODO - return something for display and/or edit roles?
        /// Right now, just return the name property
        CM_PersistentObject *p = item_list[index.row()];
        if (p)
        {
            qDebug() << "Display/Edit Role";
            return p->GetValue("name","");
        }
    }


    // We can assume it is a user role, look it up in our list
    // Get the role name and use it to lookup the value in the values hash
    if (role >= Qt::UserRole)
    {
        QString role_name = role_list[role];        
        CM_PersistentObject *p = item_list[index.row()];
        if (p)
        {
            //qDebug() << role_name << " - " << p->GetValue(role_name);
            //qDebug() << p->GetAllValues();
            return p->GetValue(role_name,"");
        }
    }
    // Example of a sub list
//    if (role == FriendsRole)
//    {
//        //// TODO - If you need to return another list?
//        //return QVariant::fromValue(static_cast<QObject*>(programs[index.row()]->friends()));
//    }


    // Unknown role
    qDebug() << "Unknown Role";
    return QVariant();
}

Qt::ItemFlags CM_PersistentObjectModel::flags(const QModelIndex &index) const
{
    if (!index.isValid())
    {
        return Qt::ItemIsEnabled;
    }

    return Qt::ItemIsEditable | QAbstractListModel::flags(index);
}

void CM_PersistentObjectModel::insert(int index, const QString &name)
{
    beginInsertRows(QModelIndex(), index, index);

    CM_PersistentObject *p = createItemObject();
    item_list.insert(index, p->CreateItem(name, parentItem()));
    delete p;

    endInsertRows();
    emit countChanged();
}

void CM_PersistentObjectModel::append(const QString &name)
{
    beginInsertRows(QModelIndex(), rowCount(), rowCount());

    CM_PersistentObject *p = createItemObject();    
    item_list.append(p->CreateItem(name, parentItem()));
    delete p;

    endInsertRows();
    emit countChanged();
}

void CM_PersistentObjectModel::remove(int index)
{
    if (index < 0 || index >= item_list.count())
    {
        qDebug() << "Can't delete non existent index: " << index;
        return;
    }
    beginRemoveRows(QModelIndex(), index, index);

    CM_PersistentObject *p = item_list.takeAt(index);
    p->DeleteObjectInfo();
    delete p;

    endRemoveRows();
    emit countChanged();

    //qDebug() << "Removed item: " << index;
}

QObject *CM_PersistentObjectModel::get(int index)
{
    if (index < 0 || index >= item_list.count())
    {
        return nullptr;
    }

    return item_list[index];
}

int CM_PersistentObjectModel::count() const
{
    return item_list.count();
}

void CM_PersistentObjectModel::setProperty(int index, const QString &property, const QVariant &value)
{
    //qDebug() << "Set Property " << property << " - " << value;

    if (index < 0 || index > item_list.count())
    {
        return;
    }

    CM_PersistentObject *p = item_list[index];
    if (p)
    {
        p->SetValue(property, value.toString());
        emit dataChanged(this->index(index), this->index(index));
    }
    /*
    if (property == "name")
    {
        programs[index]->setName(value.toString());
        emit dataChanged(this->index(index), this->index(index));
    }*/
}

bool CM_PersistentObjectModel::setData(const QModelIndex & index, const QVariant & value, int role)
{
    //qDebug() << "Edit Role " << index << " - " << value << " - " << role;

    if (index.isValid())  // && role == Qt::EditRole
    {

        CM_PersistentObject *p = item_list[index.row()];
        if (p)
        {
            QString role_name = role_list[role];
            p->SetValue(role_name, value.toString());
            p->SaveObjectInfo(); // Make sure data gets put in the db
            emit dataChanged(index, index);
            //qDebug() << "Saved info " << role_name << " - " << value;
         }


        /*
        //save value from editor to member m_gridData
        m_gridData[index.row()][index.column()] = value.toString();
        //for presentation purposes only: build and emit a joined string
        QString result;
        for(int row= 0; row < ROWS; row++)
        {
            for(int col= 0; col < COLS; col++)
            {
                result += m_gridData[row][col] + " ";
            }
        }
        emit editCompleted( result );
        */
    }
    return true;
}


