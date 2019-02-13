#ifndef CUSTOMLOGGER_H
#define CUSTOMLOGGER_H

#include <QObject>
#include <QString>
#include <QFile>
#include <QHash>
#include <QTime>
#include <QTextStream>


// Values for custom log handler
static QString log_file_path = "/debug.log";
static bool log_to_file = true;
static bool is_in_IDE = false;
static QFile log_file;

void customLogOutput(QtMsgType type, const QMessageLogContext &context,
                     const QString &msg) {
    QHash<QtMsgType, QString> msgLevelHash({{QtDebugMsg, "Debug"},
                                            {QtInfoMsg, "Info"},
                                            {QtWarningMsg, "Warning"},
                                            {QtCriticalMsg, "Critical"},
                                            {QtFatalMsg, "Fatal"}});
    QByteArray localMsg = msg.toLocal8Bit();
    QTime time = QTime::currentTime();
    QString formattedTime = time.toString("hh:mm:ss.zzz");
    QByteArray formattedTimeMsg = formattedTime.toLocal8Bit();
    QString logLevelName = msgLevelHash[type];
    QByteArray logLevelMsg = logLevelName.toLocal8Bit();

    if (log_to_file) {
        QString txt = QString("%1 %2: %3 (%4)").arg(formattedTime, logLevelName,
                                                    msg, context.file);
        if (!log_file.isOpen()) {
            log_file.setFileName(log_file_path);
            log_file.open(QIODevice::WriteOnly | QIODevice::Append);
        }

        QTextStream ts(&log_file);
        ts << txt << endl;

    } else {
        fprintf(stderr, "%s %s: %s (%s:%u, %s)\n", formattedTimeMsg.constData(),
                logLevelMsg.constData(), localMsg.constData(), context.file,
                context.line, context.function);
        fflush(stderr);
    }

    if (type == QtFatalMsg) {
        abort();
    }
}



#endif // CUSTOMLOGGER_H
