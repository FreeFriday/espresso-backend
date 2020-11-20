var express = require('express');
var router = express.Router();
const log = require('../modules/util').log;
const fs = require('fs');

//root folder for object images
//images should be in FILE_BASE/<class_name>/<image_name>
const FILE_BASE = "/home/ksw/snu/CTS/testimg";

//get object class list
/*
return json format:
{
    "list":[c1, c2, c3, ...]
}
 */

router.get('/list',function(req, res) {
    log('obj.js', "objlist list");
    fs.readdir(FILE_BASE, function(error, filelist){
        console.log(filelist);
        res.send(JSON.stringify({list:filelist}));
    })
});

//get images from class
//~~/get/<class_name>?from=<from>&to=<to>
//<from> and <to> are index numbers(both included)
/*
return json format on success:
{
    "data":[img1, img2, img3, ...]
    "error": null
}

return json format on failure due to wrong class name:
{
    "data":[]
    "error": {
        "code": "ENOENT",
        "errno": -2,
        "path": "~~",
        "syscall": "scandir"
    }
}

return json format on failure due to wrong index:
{
    "data": [],
    "error": {
        "code": "EOUTOFBOUND"
    }
}
 */
router.get('/get/:id', function(req, res) {
    const obj_class = req.params.id;
    const from = req.query.from;
    const to = req.query.to;
    log('obj.js', obj_class);
    log('obj.js', "filepath="+`${FILE_BASE}/${obj_class}`);
    fs.readdir(`${FILE_BASE}/${obj_class}`, function(error, filelist){
        var list = {data : [], error: null};

        if(error != null){
            console.log(error);
            list.error = error;
        }
        else{
            if(from<0 || to>=filelist.length){
                list.error={
                    "code": "EOUTOFBOUND"
                }
            }
            else{
                filelist.sort();
                for(var i=from; i<=to; i++){
                    var file = filelist[i];
                    console.log(`${FILE_BASE}/${obj_class}/${file}`);
                    list.data.push(fs.readFileSync(`${FILE_BASE}/${obj_class}/${file}`, 'base64'));
                }
            }
        }
        res.send(JSON.stringify(list));
        log('obj.js', "done");
    })
});

module.exports = router;