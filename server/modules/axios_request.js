const FormData = require('form-data');
const axios = require('axios');
const fs = require('fs');

const axiosRequest = async (filePath)=>{
  var newFile = fs.createReadStream(filePath);
  const formData = new FormData();
  formData.append("img", newFile, newFile.name);
  try{
    var response = await axios.create({headers: formData.getHeaders()}).post("http://127.0.0.1:5000/inference", formData);
    return response.data
  } catch(e){
    console.log("[ERROR|axiosRequest] ", e) ;
    return error
  }
};
module.exports = axiosRequest;