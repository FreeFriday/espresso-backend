function getNow() {
    const today = new Date();

    const dayNames = ['(일요일)', '(월요일)', '(화요일)', '(수요일)', '(목요일)', '(금요일)', '(토요일)'];
    // const day = dayNames[today.getDay()];

    const year = today.getFullYear();
    const month = today.getMonth() + 1;
    const date = today.getDate();
    let hour = today.getHours();
    let minute = today.getMinutes();
    let second = today.getSeconds();

    // const ampm = hour >= 12 ? 'PM' : 'AM';
    // hour %= 12;
    // hour = hour || 12; // 0 => 12

    minute = minute < 10 ? '0' + minute : minute;
    second = second < 10 ? '0' + second : second;

    const now = `${year}-${month}-${date}_${hour}:${minute}:${second}`;

    return now
}


function log(name, msg) {
    const msg_ = `[${getNow()} | ${name}] ${msg}`;
    console.log(msg_)
}

exports.getNow = getNow;
exports.log = log;