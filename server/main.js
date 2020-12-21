const express = require('express');
const app = express();
const transfer_router = require('./routes/transfer').router;
const compose_router = require('./routes/compose');
const pp_router = require('./routes/postprocessor').router;
const pool_router = require('./routes/pool');
const test_router = require('./routes/test');
const obj_router = require('./routes/obj');
const painter_router = require('./routes/painter');
const random_router = require('./routes/random').router;

const PORT = 8080;

app.use('/transfer', transfer_router);
app.use('/compose', compose_router);
app.use('/postprocessor', pp_router);
app.use('/pool', pool_router);
app.use('/test', test_router);
app.use('/obj', obj_router);
app.use('/painter', painter_router);
app.use('/random', random_router);

app.listen(PORT,'0.0.0.0', () => {
    console.log(`listening at ${PORT}`)
});
