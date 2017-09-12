#ifndef DB_H
#define DB_H

#include <QObject>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QtSql>
#include <QSqlDatabase>
#include <QSqlQueryModel>
#include <QSqlTableModel>
#include <QSqlRecord>
#include <QSqlResult>
#include <QSqlField>
#include <QHash>
#include <QCryptographicHash>

class APP_DB;
class GenericQueryModel;
class GenericTableModel;

/**
 * @brief The GenericQueryModel class
 * Used to create generic queries for QML controls
 */
class GenericQueryModel : public QSqlQueryModel {
    Q_OBJECT
public:
    explicit GenericQueryModel(APP_DB *parent=0, QString query_name="", QString query="", QSqlDatabase db = QSqlDatabase());
    void refresh();

signals:

public slots:

    QVariant data(const QModelIndex &index, int role) const;
    QHash<int, QByteArray> roleNames() const { return m_roleNames; }

    void modifyQuery(QString q);
    void modifyFilter(QString f, bool combine_w_and=true);

    QHash<QString, QVariant> getRecord(int row) const;
    QString getColumnName(int col_index);
    int getColumnIndex(QString col_name);


private:
    void generateRoleNames();
    void setCombinedQuery();

    QString m_query_name;
    QHash<int, QByteArray> m_roleNames;
    QString m_sql_select;
    QString m_filter;
    bool m_combine_filter_w_and;
};


/**
 * @brief The GenericTableModel class
 * Used to create generic models for QML controls
 */
class GenericTableModel : public QSqlTableModel {
    Q_OBJECT
public:
    explicit GenericTableModel(APP_DB *parent=0, QString table_name="", QSqlDatabase db = QSqlDatabase());

public slots:
    void setTable(QString tableName);

    QVariant data(const QModelIndex &index, int role) const;
    QHash<int, QByteArray> roleNames() const { return m_roleNames; }

    // A slot that exposes set filter to QML code
    void modifyFilter(QString f);
    QHash<QString, QVariant> getRecord(int row) const;
    QString getColumnName(int col_index);
    int getColumnIndex(QString col_name);

private:
    void generateRoleNames();

    QHash<int, QByteArray> m_roleNames;

};



/**
 * @brief Controls DB access, deals with migration, and exposes models to QML
 *
 */
class APP_DB : public QObject
{
    Q_OBJECT
public:
    explicit APP_DB(QQmlApplicationEngine *parent = 0);

    static QQmlEngine *_engine;

    QHash<QString, GenericTableModel *> _tables;
    QHash<QString, GenericQueryModel *> _queries;

signals:

public slots:

    bool init_db();

    // == USER FUNCTIONS ==
    bool auth_student(QString user_name, QString password);


    // == RESOURCE FUNCTIONS ==
    bool add_resource(QString resource_name, QString resource_url, QString resource_description, int sort_order);

    GenericTableModel *getTable(QString table_name);
private:

    QSqlDatabase _db;


};

#endif // DB_H
