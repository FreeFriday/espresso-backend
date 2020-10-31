var express = require('express');
var router = express.Router();

router.post('/compose', function(req, res) {
  res.send('hi');
});

module.exports = router;