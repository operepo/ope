#ifndef CM_PERSISTENTOBJECT_H
#define CM_PERSISTENTOBJECT_H

#include <QObject>
#include <QtSql>
#include <QHash>
#include <QMultiHash>
#include <QList>
#include <QDebug>

class CM_PersistentObject : public QObject
{
    Q_OBJECT

protected:
    QHash<QString, QString> _VALUES;
    QHash<QString, bool> _CHANGED_VALUES;
    QString object_type;
    QString _parent_item;

    bool db_open;
    QSqlDatabase db;
    QString db_id;
    QString db_name;
    QString table_name;
    QString identifier_field;
    QString site_id;

public:

    static QString db_folder;

    explicit CM_PersistentObject(QObject *parent = 0);

    virtual CM_PersistentObject* createItemObject(QObject *parent = 0)
    {
        //qDebug() << "CM_PersistentObject - createItemObject";
        CM_PersistentObject *p = new CM_PersistentObject(parent);
        return p;
    }

    Q_PROPERTY(QSqlDatabase database READ database WRITE setDatabase NOTIFY databaseChanged)
    Q_PROPERTY(QString DBName READ DBName WRITE setDBName NOTIFY DBNameChanged)
    Q_PROPERTY(QString table_name READ TableName WRITE setTableName NOTIFY TableNameChanged)
    Q_PROPERTY(QString IdentifierField READ IdentifierField WRITE setIdentifierField NOTIFY IdentifierFieldChanged)

signals:
    void databaseChanged(QSqlDatabase);
    void DBNameChanged(QString);
    void TableNameChanged(QString);
    void IdentifierFieldChanged(QString);

public slots:
    bool DBConnect();
    QString Escape(QString value);

    QSqlDatabase database();
    void setDatabase(QSqlDatabase database);

    QString DBName();
    void setDBName(QString name);

    QString TableName();
    void setTableName(QString name);

    QString IdentifierField();
    void setIdentifierField(QString name);

    void SetParentItem(QString parent_item);

    void ClearValues();

    QList<QString> GetKeys();

    QList<CM_PersistentObject*> GetItemList(QString parent_item = "");

    CM_PersistentObject * CreateItem(QString name, QString parent_item = "");

    bool ItemExists(QString name);

    QString SetValueIfNotExists(QString key, QString value, bool set_value_dirty = true);

    QString SetValue(QString key, QString value, bool set_value_dirty = true);

    void SetValueDirty(QString key);

    void SetIDValue(QString id_value);

    QString GetIDValue();

    void SetTableName(QString table_name);

    QString GetTableName();

    QHash<QString, QString> GetAllValues();

    QString GetValue(QString key, QString default_value = "");

    bool LoadObjectInfo();
    bool SaveObjectInfo();

    void DeleteObjectInfo();

    bool EnsureTableExists();

protected:
    bool SaveValueToDatabase(QString key="", QString value="", bool clear_value = true);

};

#endif // CM_PERSISTENTOBJECT_H

