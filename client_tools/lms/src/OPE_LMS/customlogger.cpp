#include "customlogger.h"

QTextStream& qStdout()
{
    static QTextStream r{stdout};
    return r;
}

QTextStream& qStderr()
{
    static QTextStream r{stderr};
    return r;
}


void customLogOutput(QtMsgType type, const QMessageLogContext &context,
                     const QString &msg) {

    // Hide warnings - is_in_IDE not used
    if(is_in_IDE) {}

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

        if (log_file.isOpen()) {
            QTextStream ts(&log_file);
            ts << txt << Qt::endl;
        } else {
            // Couldn't open log? Send to stdout
            err << "[log open error] " << txt << Qt::endl;
        }

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
