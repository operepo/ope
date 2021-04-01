#ifndef CUSTOMLOGGER_H
#define CUSTOMLOGGER_H

#include <QObject>
#include <QString>
#include <QFile>
#include <QHash>
#include <QTime>
#include <QTextStream>

QTextStream& qStdout();

QTextStream& qStderr();

// Values for custom log handler
static QString log_file_path = "/debug.log";
static bool log_to_file = true;
static bool is_in_IDE = false;
static QFile log_file;
static QTextStream &out = qStdout();
static QTextStream &err = qStderr();
// Are we running in quiet mode?
static bool quiet_mode = false;

void customLogOutput(QtMsgType type, const QMessageLogContext &context,
                     const QString &msg);


#endif // CUSTOMLOGGER_H
