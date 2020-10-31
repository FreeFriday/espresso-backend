const express = require('express');
const router = express.Router();
const multer_option = require('../modules/multer_option');
const FormData = require('form-data');
const fs = require('fs');
const request = require('request');
// var multipart = require('connect-multiparty');
// var mp_middleware = multipart();


router.post('/', multer_option.single('img'), async (req, res) => {
    fileName = req.file['filename'];

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
                res.json({
                    status: true,
                    elapsed_time: body['elapsed_time'],
                    img: body['img'],
                });
            } else {
                res.json({
                    success: false,
                    message: body['message']
                });
            }
        } catch (e) {
            console.log("[ERROR|axios_response] : ", e)
        }
    });
});
module.exports = router;