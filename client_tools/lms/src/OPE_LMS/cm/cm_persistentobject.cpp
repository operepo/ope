#include "cm_persistentobject.h"

QString CM_PersistentObject::db_folder = ""; // QDir::currentPath();

CM_PersistentObject::CM_PersistentObject(QObject *parent) :
    QObject(parent)
{
    //qDebug() << "CM_PersistentObject - Constructor";

    db_open = false;
    db_id = "pobject";
    db_name = "cm_object.db";
    table_name = "pobject_items";
    identifier_field = "object_id";
    object_type = "PersistentObject";
    site_id = "DEFAULT_SITE";

    // Make sure the table exists to hold this object
    EnsureTableExists();   
}

bool CM_PersistentObject::DBConnect()
{
    bool ret = true;

    if (!db_open) {
        if (QSqlDatabase::connectionNames().contains(db_id)) {
            db = QSqlDatabase::database(db_id, true);

            //qDebug() << "Reusing Db: ";
        } else {
            db = QSqlDatabase::addDatabase("QSQLITE", db_id);
            QString db_path = db_name;
            if (CM_PersistentObject::db_folder != "")
            {
                db_path = CM_PersistentObject::db_folder + QDir::separator() + db_path;
            }
            qDebug() << "DB Path: " << db_path;
            db.setDatabaseName(db_path);
            db_open = ret = db.open();


            //qDebug () << "Database opened: " << db_name;
        }
    }

    return ret;
}

QString CM_PersistentObject::Escape(QString value)
{
    return db.driver()->escapeIdentifier(value, QSqlDriver::FieldName);
    //return value.replace("'", "\'").replace("`", "\`");
}

QSqlDatabase CM_PersistentObject::database() { return db; }
void CM_PersistentObject::setDatabase(QSqlDatabase database) { db = database; }

QString CM_PersistentObject::DBName() { return db_name; }
void CM_PersistentObject::setDBName(QString name) { db_name = name; }

QString CM_PersistentObject::TableName() { return table_name; }
void CM_PersistentObject::setTableName(QString name) { table_name = name; }

QString CM_PersistentObject::IdentifierField() { return identifier_field; }
void CM_PersistentObject::setIdentifierField(QString name) { identifier_field = name; }

void CM_PersistentObject::SetParentItem(QString parent_item)
{
    _parent_item = parent_item;
}

void CM_PersistentObject::ClearValues()
{
    _VALUES.clear();
    _CHANGED_VALUES.clear();

}

QList<QString> CM_PersistentObject::GetKeys()
{
    return _VALUES.keys();
}

QList<CM_PersistentObject*> CM_PersistentObject::GetItemList(QString parent_item)
{
    QList<CM_PersistentObject*> list;
    CM_PersistentObject *p;

    if (!DBConnect()) { qDebug() << "Database error in GetItemList"; return list; }

    QString sql = "SELECT `object_id` FROM " + Escape(table_name)
            + " WHERE `site_id`=:site_id "
            + " AND `object_type`=:object_type"
            + " AND  `key`=:key";
    if (parent_item != "")
    {
        sql += " AND `parent_id`=:parent_id";
    }
    QSqlQuery rs(db);
    rs.prepare(sql);
    rs.bindValue(":site_id", site_id);
    rs.bindValue(":object_type", object_type);
    rs.bindValue(":key", "name");
    if (parent_item != "")
    {
        rs.bindValue(":parent_id", parent_item);
    }
    if (!rs.exec()) {
        qDebug() << "Error getting item list! " << rs.lastError().text() << " - " << rs.lastQuery();
        return list;
    }

    while (rs.next())
    {
        p = createItemObject(); // new CM_PersistentObject();
        p->SetIDValue(rs.value("object_id").toString());
        p->LoadObjectInfo();
        list.append(p);
    }

    return list;
}

CM_PersistentObject * CM_PersistentObject::CreateItem(QString name, QString parent_item)
{
    CM_PersistentObject * ret = nullptr;

    if (!ItemExists(name))
    {
        ret = createItemObject(); // new CM_PersistentObject();
        ret->SetIDValue(name);
        ret->SetValue("name", name);
        ret->SetParentItem(parent_item);
        ret->SaveObjectInfo();

        //// TODO emit datachanged?
        //emit dataChanged();
    }

    return ret;
}

bool CM_PersistentObject::ItemExists(QString name)
{
    bool ret = false;

    if (!DBConnect()) { qDebug() << "Database error in ItemExists"; return ret; }

    QString sql = "SELECT `object_id` FROM " + Escape(table_name)
            + " WHERE `site_id`=:site_id "
            + " AND `object_type`=:object_type"
            + " AND `key`=:key"
            + " AND `value`=:value";
    QSqlQuery rs(db);
    rs.prepare(sql);
    rs.bindValue(":site_id", site_id);
    rs.bindValue(":object_type", object_type);
    rs.bindValue(":key", "name");
    rs.bindValue(":value", name);
    if (!rs.exec()) {
        qDebug() << "Error in ItemExists! " << rs.lastError().text() << " - " << rs.lastQuery();
        return ret;
    }

    while (rs.next())
    {
        // If we have ANY records, the item exists
        ret = true;
    }

    return ret;
}

QString CM_PersistentObject::SetValueIfNotExists(QString key, QString value, bool set_value_dirty) {
    QString val = GetValue(key, "");
    if (val != "") { return ""; }
    return SetValue(key, value, set_value_dirty);
}

QString CM_PersistentObject::SetValue(QString key, QString value, bool set_value_dirty ) {
    bool changed = false;
    if (key.endsWith("[]")) {
        // TODO Don't support arrays at this point
        /*
        // This is an array value, store it as such
        QList<QString> arr;
        if (_VALUES.contains(key)) {
            arr = _VALUES[key];
        }

        if (!arr.contains(value)) {
            // Don't add a value twice
            arr.push_back(value);
            changed = true;
        }
        _VALUES[key] = arr;
        */
    } else {
        if (!_VALUES.contains(key) || _VALUES[key] != value) {
            changed = true;
            _VALUES[key] = value;
        }
    }

    if (set_value_dirty == true && changed == true) {
        SetValueDirty(key);
    }

    return value;
}

void CM_PersistentObject::SetValueDirty(QString key) {
    if(!_CHANGED_VALUES.contains(key)) {
         _CHANGED_VALUES[key] = true;
    }
}

void CM_PersistentObject::SetIDValue(QString id_value) {
    SetValue(identifier_field, id_value, false);
}

QString CM_PersistentObject::GetIDValue() {
    if (identifier_field == "") { return ""; }
    return GetValue(identifier_field, "");
}

void CM_PersistentObject::SetTableName(QString table_name) {
    SetValue("cmtk_persistent_save_table", table_name, false);
}

QString CM_PersistentObject::GetTableName() {
    return GetValue("cmtk_persistent_save_table", table_name);
}

QHash<QString, QString> CM_PersistentObject::GetAllValues() {
    return _VALUES;
}

QString CM_PersistentObject::GetValue(QString key, QString default_value) {
    if (_VALUES.contains(key)) {
        return _VALUES[key];
    }
    return default_value;
}

bool CM_PersistentObject::LoadObjectInfo() {
    // Get the page info from the database
    if (!DBConnect()) { return false; }

    QString table_name = GetTableName();    
    QString id_field = IdentifierField();
    QString id_value = GetValue(id_field, "");
    QString sql = "SELECT * FROM " + Escape(table_name)
            + " WHERE `site_id`=:site_id AND "
            + "`object_type`=:object_type AND "
            + Escape(id_field) + "=:id_value";

    QSqlQuery rs(db);
    //qDebug() << sql << " - " << id_value << " - " << object_type << " - " << site_id;
    rs.prepare(sql);
    rs.bindValue(":site_id", site_id);
    rs.bindValue(":object_type", object_type);
    rs.bindValue(":id_value", id_value);

    if (!rs.exec()) {
        qDebug() << rs.lastError().text() << " - " << rs.lastQuery();
    }

    while (rs.next()) {        
        SetValue(rs.value("key").toString(), rs.value("value").toString(), false);
        _parent_item = rs.value("parent_id").toString();
        //qDebug() << "Got Value: " << rs.value("key").toString() << " - " << rs.value("value").toString();
    }
    return true;
}

bool CM_PersistentObject::SaveObjectInfo() {
    // Store the page info in the database

    foreach (QString key, _VALUES.keys()) {
        // Only save keys that have changed
        if (_CHANGED_VALUES.contains(key))
        {
            SaveValueToDatabase(key, _VALUES[key]);
        }
    }

    // Clear the changed values array
    _CHANGED_VALUES.clear();

    return true;
}

void CM_PersistentObject::DeleteObjectInfo()
{
    // Delete the current object
    if (!DBConnect()) { return; }

    QString table_name = GetTableName();
    QString id_field = IdentifierField();
    QString id_value = GetValue(id_field, "");
    QString sql = "DELETE FROM " + Escape(table_name)
            + " WHERE `site_id`=:site_id AND "
            + "`object_type`=:object_type AND "
            + Escape(id_field) + "=:id_value";

    QSqlQuery rs(db);
    rs.prepare(sql);
    rs.bindValue(":site_id", site_id);
    rs.bindValue(":object_type", object_type);
    rs.bindValue(":id_value", id_value);

    if (!rs.exec()) {
        qDebug() << rs.lastError().text() << " - " << rs.lastQuery();
    }
}

bool CM_PersistentObject::SaveValueToDatabase(QString key, QString value, bool clear_value)
{
    if (!DBConnect()) { return false; }

     QString table_name = GetTableName();
     QString id_field = IdentifierField();
     QString id_value = GetValue(id_field, "");

     QString sql;

     // Save simple value
     // Clear this value
     if (clear_value == true) {         
         sql = "DELETE FROM " + Escape(table_name)
                 + " WHERE `site_id`=:site_id AND "
                 "`object_type`=:object_type AND "
                 + Escape(id_field) + "=:id_value AND "
                 "`key`=:key";

         QSqlQuery rs(db);
         rs.prepare(sql);         
         rs.bindValue(":site_id", site_id);
         rs.bindValue(":object_type", object_type);         
         rs.bindValue(":id_value", id_value);
         rs.bindValue(":key", key);

         if (!rs.exec()) {
             qDebug() << rs.lastError().text() << " - " << rs.lastQuery();
         }
         //qDebug() << "Values cleared: " << id_value << " - " << key;
     }

     // Add this value to the database
     sql = "INSERT INTO " + Escape(table_name)
             + " (`site_id`, `object_type`, " + Escape(id_field)
             + " , `parent_id`, `key`, `value`) VALUES (:site_id, :object_type,"
             + " :id_value, :parent_id, :key, :value)";
     QSqlQuery rs(db);
     rs.prepare(sql);     
     rs.bindValue(":site_id", site_id);
     rs.bindValue(":object_type", object_type);
     rs.bindValue(":id_value", id_value);
     rs.bindValue(":parent_id", _parent_item);
     rs.bindValue(":key", key);
     rs.bindValue(":value", value);

     if (!rs.exec()) {
         qDebug() << rs.lastError().text() << " - " << rs.lastQuery();
     }
     //qDebug() << "Value Saved: " << key << " - " << value;


     //// TODO: Do not support array values at this time - use multihash???
     /*
     // Add this value to the database
     $sql = "INSERT INTO `$table_name` (`site_id`, `$id_field`, `key`, `value`) " .
         " VALUES ('$site_id', '$id_value', " .
         "'" . cmtk_EscapeString($key) . "', " .
         "'" . cmtk_EscapeString($value) . "')";
     cmtk_Query($sql);

     if (substr(key, -2) == "[]" && is_array($value)) {
        // Clear the values for this array before saving it
        $sql = "DELETE FROM `$table_name` WHERE `site_id`='$site_id' AND" .
            " `$id_field`='$id_value' AND `key`='$key'";
        cmtk_Query($sql);
        // This is an array value, call this function recursively to save the array items.
        foreach ((array)$value as $tkey=>$tval) {
            if(!is_numeric($tkey) && strlen($tken) > 0) {
                $key = $key . "_" . $tkey;
            }
            // Don't clear the value though as there will be multiples
            $this->SaveValueToDatabase($identifier_field1, $identifier_value1, $key, $tval, false, $table_name);
        }
    } else {
        // Save simple value
        // Clear this value
        if ($clear_value == true) {
            $sql = "DELETE FROM `$table_name` WHERE `site_id`='$site_id' AND" .
                " `$id_field`='$id_value' AND `key`='$key'";
            cmtk_Query($sql);
        }

        // Add this value to the database
        $sql = "INSERT INTO `$table_name` (`site_id`, `$id_field`, `key`, `value`) " .
            " VALUES ('$site_id', '$id_value', " .
            "'" . cmtk_EscapeString($key) . "', " .
            "'" . cmtk_EscapeString($value) . "')";
        cmtk_Query($sql);
    }
    */
     return true;
}

bool CM_PersistentObject::EnsureTableExists()
{
    bool ret = true;

    if (!DBConnect()) { return false; }

    QString sql = "CREATE TABLE IF NOT EXISTS " + Escape(table_name)
            + " (`id` CHAR(36), `site_id` TEXT, `object_type` TEXT,"
            + " `object_id` TEXT, `parent_id` TEXT, `key` TEXT, `value` TEXT)";



    QSqlQuery rs(db);
    if (!rs.exec(sql)) {
        qDebug() << rs.lastError().text() << " - " << rs.lastQuery();
    }

    //qDebug() << "Table Exists: " << table_name;

    ////TODO: Add indexes
    ///

    return ret;
}

