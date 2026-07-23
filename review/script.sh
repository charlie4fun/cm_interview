STDOUT="/dev/stdout"
LOG_FILE='$STDOUT'
LOG_MESSAGE='is the date, should log to $STDOUT'

# log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"
}

log_message $LOG_MESSAGE
