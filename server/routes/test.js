const express = require('express');
const router = express.Router();
const log = require('../modules/util').log;

router.get('/', function(req, res) {
    log('test.js', 'entry');
    res.send('hi');
});

module.exports = router;
