var express = require('express');
var router = express.Router();


router.get('/demo', function(req, res) {
   res.sendFile('/home/freefridays/github/espresso-backend/debug/upload_server2.html');
});

router.get('/author/:id', function(req, res) {
    const id = req.params.id;
    res.send(`${id}`);
});

module.exports = router;
