const express = require('express');
const router = express.Router();
const fs = require('fs');
const request = require('request');
const log = require('../modules/util').log;


router.get('/', function(req, res) {
   res.sendFile('/home/freefridays/github/espresso-backend/debug/random_generator.html');
});


router.get('/generator', function(req, res) {
    const bgremove = req.query.bgrmv;
    const am = req.query.am;
    const amft = req.query.amft;
    const ambt = req.query.ambt;
    const amess = req.query.amess;

    log('random.js');
    const opt = {
        uri: 'http://127.0.0.1:5000/random?bgrmv='+bgremove+"&am="+am+"&amft="+amft+"&ambt="+ambt+"&amess="+amess,
        method: 'GET'
    };
    log('random.js', "uri="+opt.uri)
    request(opt, (err, resp, body) => {
        // body: json string response
        try {
            log('random.js', 'flask response: ' + toString(resp.statusCode));
            body = JSON.parse(body);
            if (body['status']) {
                log('random.js', 'success');
                res.json({
                    status: true,
                    elapsed_time: body['elapsed_time'],
                    img_in: body['img_in'],
                    img_out: body['img_out'],
                });
            } else {
                log('random.js');
                res.json({
                    success: false,
                    message: body['message']
                });
            }
        } catch (e) {
            log('random.js',  `ERROR: ${e}`);
            res.sendStatus(500)
        }
    });
});
module.exports.router = router;