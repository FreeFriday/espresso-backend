const express = require('express');
const router = express.Router();
const multer_option = require('../modules/multer_option');
const FormData = require('form-data');
const fs = require('fs');
const request = require('request');
const log = require('../modules/util').log;
// var multipart = require('connect-multiparty');
// var mp_middleware = multipart();
const TEMP_FILE_BASE = "/home/freefridays/TempResults"

router.post('/', multer_option.single('img'), async (req, res) => {
    if(!req.file){
        res.sendStatus(400)
    }
    fileName = req.file['filename'];
    const bgremove = req.query.bgrmv;
    const am = req.query.am;
    const amft = req.query.amft;
    const ambt = req.query.ambt;
    const amess = req.query.amess;

    log('transfer.js', 'entry: ' + fileName);
    const newFile = fs.createReadStream('./uploaded/' + fileName);
    const opt = {
        uri: 'http://127.0.0.1:5000/inference?bgrmv='+bgremove+"&am="+am+"&amft="+amft+"&ambt="+ambt+"&amess="+amess,
        method: 'POST',
        formData: {
            'img': newFile
        }
    };
    log('transfer.js', "uri="+opt.uri)
    request(opt, (err, resp, body) => {
        // body: json string response
        try {
            log('transfer.js', 'flask response: ' + toString(resp.statusCode));
            body = JSON.parse(body);
            if (body['status']) {
                log('transfer.js', 'success:' + fileName);
                fs.writeFileSync(TEMP_FILE_BASE+"/"+fileName, body['img'], 'base64')
                res.json({
                    status: true,
                    elapsed_time: body['elapsed_time'],
                    img: body['img'],
                    img_name: fileName
                });
            } else {
                log('transfer.js', 'reading body failed: ' + fileName);
                res.json({
                    success: false,
                    message: body['message']
                });
            }
        } catch (e) {
            log('transfer.js',  `ERROR: ${e}`, fileName);
            res.sendStatus(500)
        }
    });
});
module.exports.TEMP_FILE_BASE = TEMP_FILE_BASE
module.exports.router = router;