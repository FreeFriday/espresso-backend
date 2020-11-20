const express = require('express');
const app = express();
const transfer_router = require('./routes/transfer');
const compose_router = require('./routes/compose');
const pp_router = require('./routes/postprocess');
const pool_router = require('./routes/pool');
const test_router = require('./routes/test');
const obj_router = require('./routes/obj');

const PORT = 2021;

app.use('/transfer', transfer_router);
app.use('/compose', compose_router);
app.use('/pp_router', pp_router);
app.use('/pool', pool_router);
app.use('/test', test_router);
app.use('/obj', obj_router);

app.listen(PORT, () => {
    console.log(`listening at ${PORT}`)
});
