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

extern QString log_file_path;
extern bool log_to_file;
extern bool is_in_IDE;
extern QFile log_file;
extern QTextStream &out;
extern QTextStream &err;
// Are we running in quiet mode?
extern bool quiet_mode;

void customLogOutput(QtMsgType type, const QMessageLogContext &context,
                     const QString &msg);


#endif // CUSTOMLOGGER_H
