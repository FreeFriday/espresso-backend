const express = require('express');
const router = express.Router();
const axios_request = require('../modules/axios_request');
const multer_option = require('../modules/multer_option');
//const request = require('request');
// var multipart = require('connect-multiparty');
// var mp_middleware = multipart();


router.post('/', multer_option.single('img'), async (req, res) => {
    fileName = requset.file['filename'];
    var axios_response = await axios_request('uploaded/' + fileName);
    console.log("[axios_response] : ", axios_response);

    try {
        if (axios_response['status']) {
            res.json({
                status: true,
                elapsed_time: axios_response['elapsed_time'],
                img: axios_response['img'],
            });
        } else {
            res.json({
                success: false,
                message: axios_response['message']
            });
        }
    } catch (e) {
        console.log("[ERROR|axios_response] : ", e)
    }}

// console.log('contentType: ', req.headers['content-type']);
//
// console.log(req.body)
// console.log()
// console.log(req.files)
//
// req.files['img']
);
module.exports = router;