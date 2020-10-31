var express = require('express');
var router = express.Router();

router.get('/:id', function(req, res) {
    const id = req.params.id;
    res.send(`${id}`);
});

module.exports = router;
