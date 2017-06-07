#include "cm_machine.h"

CM_Machine::CM_Machine(QObject *parent) :
    QObject(parent)
{
    // Init class variables
    //con_string = ":memory:"; // Use this if you want it to forget your database when the app closes
    con_string = "sysmange.db";
    db_init = false;
    db_connected = false;
    possible_machine_ids.clear();
    mac_addresses.clear();
    machine_id = "";

    // Make sure that we generate the current machine id
    CalculateMachineID();

    // Ready the database
    InitDB();

}

void CM_Machine::CalculateMachineID()
{
    if (machine_id != "") { return; }

    // Generate the id of the current machine by grabbing the mac address of this
    // machine

    mac_addresses.clear();
    QString mac_addr = "";
    QList<QNetworkInterface> if_list = QNetworkInterface::allInterfaces();
    foreach (QNetworkInterface interface, if_list)
    {
        mac_addr = interface.hardwareAddress();
        // We don't want this if it is the loopback addr or if it is empty

        if (!(interface.flags() & QNetworkInterface::IsLoopBack) &&
                !mac_addr.startsWith("00:00:00:00:00:00:00") &&
                mac_addr != "")
        {
            qDebug() << "Found MAC: " << mac_addr;
            mac_addresses.append(mac_addr);
        }
    }

    // Create GUIDs for each mac address
    CalculatePossibleMachineIDs();

    // Look for one of these ids in the machine_ids table
    QString sql;
    sql = "SELECT * FROM `machine_ids` WHERE `guid`=@guid";

    QSqlQuery query;

    query.prepare(sql);
    bool found_machine_id = false;
// TODO
    foreach(QString mid, possible_machine_ids)
    {
        // Does this id already exist?
        query.bindValue("@guid", mid);
        query.exec();
        if (query.numRowsAffected() > 0)
        {
            // Found one
            found_machine_id = true;
        }

    }


    qDebug() << "Final Machine ID: " << machine_id;
}

void CM_Machine::CalculatePossibleMachineIDs()
{
    // Use the current mac address list and hardware info to
    // calculate possible machine ids for this system

    // Clear the current list
    possible_machine_ids.clear();

    foreach (QString mac, mac_addresses)
    {
        // Convert this mac to a byte array
        QByteArray arr = mac.toLatin1();

        // Get an SHA1 hash of this
        QCryptographicHash *hash = new QCryptographicHash(QCryptographicHash::Sha1);
        arr = hash->hash(arr, QCryptographicHash::Sha1);

        // Make sure we have exactly 16 bytes (use x as a place holder)
        arr = arr.leftJustified(16, 'x', true);

        // Make a GUID of this
        QUuid uid = QUuid::fromRfc4122(arr);
        possible_machine_ids.append(uid.toString());
        qDebug() << "Mac Address: " << mac << " UUID: " << uid.toString();
    }

}

bool CM_Machine::IsNetworkActive()
{
    // See if any networks are active
    bool active = false;

    QString mac_addr = "";
    QList<QNetworkInterface> if_list = QNetworkInterface::allInterfaces();
    foreach(QNetworkInterface interface, if_list)
    {
        mac_addr = interface.hardwareAddress();
        if (!(interface.flags() & QNetworkInterface::IsLoopBack) &&
                !mac_addr.startsWith("00:00:00:00:00:00:00") &&
                interface.flags() & QNetworkInterface::IsUp)
        {
            // This network is up
            active = true;
            qDebug() << "Interface is up: " << interface.hardwareAddress();
        }
    }

    return active;
}

void CM_Machine::InitDB() {
    QSqlDatabase db;
    if (!db_connected) {
        db = QSqlDatabase::addDatabase("QSQLITE");
        db.setDatabaseName(con_string);
        if(!db.open()) {
//            QMessageBox::critical(0, tr("Cannot open database"),
//                tr("Unable to establish a database connection.\n"
//                   "This example needs SQLite support. Please read "
//                   "the Qt SQL driver documentation for information how "
//                   "to build it."), QMessageBox::Cancel);
            return;
        }
        db_connected = true;
    }

    if (!db_init) {
        // Make sure that the tables and such exist
        QString sql = "CREATE TABLE IF NOT EXISTS `machines` (guid char(36) NOT NULL UNIQUE, MachineName char(300) ) ";

        QSqlQuery query;
        query.exec(sql);

        // Add a list of mac addresses for this machine
        sql = "CREATE TABLE IF NOT EXISTS `machine_ids` (guid char(36) NOT NULL UNIQUE, ParentMachine char(36))";
        query.exec(sql);

        db_init = true;
    }


}
