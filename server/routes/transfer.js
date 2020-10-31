const express = require('express');
const router = express.Router();
const multer_option = require('../modules/multer_option');
const FormData = require('form-data');
const fs = require('fs');
const request = require('request');
const log = require('../modules/util').log;
// var multipart = require('connect-multiparty');
// var mp_middleware = multipart();


router.post('/', multer_option.single('img'), async (req, res) => {
    fileName = req.file['filename'];

    log('transfer.js entry', fileName);

    const newFile = fs.createReadStream('./uploaded/' + fileName);
    const opt = {
        uri: 'http://127.0.0.1:5000/inference',
        method: 'POST',
        formData: {
            'img': newFile,
        }
    };
    request(opt, (err, resp, body) => {
        // body: json string response
        console.log("[axios_response] : ", resp.statusCode);
        body = JSON.parse(body);
        try {
            if (body['status']) {
                log('transfer.js success', fileName);
                res.json({
                    status: true,
                    elapsed_time: body['elapsed_time'],
                    img: body['img'],
                });
            } else {
                log('transfer.js reading body failed', fileName);
                res.json({
                    success: false,
                    message: body['message']
                });
            }
        } catch (e) {
            log(`transfer.js ERROR ${e}`, fileName);
        }
    });
});
module.exports = router;