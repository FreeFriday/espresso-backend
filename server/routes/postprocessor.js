const express = require('express');
const router = express.Router();
const multer_option = require('../modules/multer_option');
const FormData = require('form-data');
const fs = require('fs');
const request = require('request');
const log = require('../modules/util').log;
const TEMP_FILE_BASE = "/home/freefridays/TempResults";

router.post('/', multer_option.single('img'), async (req, res) => {
    if(!req.file){
        res.sendStatus(400)
    }
    fileName = req.file['filename'];
    const H = req.query.h;
    const W = req.query.w;
    const level = req.query.level; // {1, 2, 3, 4, 5}
    const bi = req.query.bi;  // {0, 1}

    log('postprocessor.js', 'entry: ' + fileName);
    const newFile = fs.createReadStream('./uploaded/' + fileName);
    const opt = {
        uri: 'http://127.0.0.1:5000/postprocess?h='+H+"&w="+W+"&level="+level+"&bi="+bi,
        method: 'POST',
        formData: {
            'img': newFile
        }
    };
    log('postprocessor.js', "uri="+opt.uri)
    request(opt, (err, resp, body) => {
        // body: json string response
        try {
            log('postprocessor.js', 'flask response: ' + toString(resp.statusCode));
            body = JSON.parse(body);
            if (body['status']) {
                log('postprocessor.js', 'success:' + fileName);
                fs.writeFileSync(TEMP_FILE_BASE+"/"+fileName, body['img'], 'base64');
                res.json({
                    status: true,
                    elapsed_time: body['elapsed_time'],
                    img: body['img'],
                    img_name: fileName
                });
            } else {
                log('postprocessor.js', 'reading body failed: ' + fileName);
                res.json({
                    success: false,
                    message: body['message']
                });
            }
        } catch (e) {
            log('postprocessor.js',  `ERROR: ${e}`, fileName);
            res.sendStatus(500)
        }
    });
});
module.exports.TEMP_FILE_BASE = TEMP_FILE_BASE;
module.exports.router = router;