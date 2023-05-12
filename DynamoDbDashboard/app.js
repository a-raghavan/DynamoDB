var express = require('express');
var bodyParser = require('body-parser');

var app = express();

// Use Images icon
app.use(express.static(__dirname + '/public'));

//using ejs
app.set('view engine', 'ejs');

app.use(bodyParser.urlencoded({ extended: true }));

//using grpc
var PROTO_PATH = __dirname + './../protos/consistentHashing.proto';
var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {keepCase: true,
     longs: String,
     enums: String,
     defaults: true,
     oneofs: true
    });
var database_proto = grpc.loadPackageDefinition(packageDefinition).consistentHashing;
var grpcClient = new database_proto.ConsistentHashing("127.0.0.1:50055", grpc.credentials.createInsecure()) 

// var grpcdata ={}


//Api Calls
// app.get('/', async function (req, res) {
//     // if(!data){
//         var promises=receiveGrpcData()
//         Promise.all(promises).then((values) => {
//             for(data in values){
//                 grpcdata[appSettings[data]]=values[data]
//             }
//             res.render('pages/index', {data: grpcdata, errormsg: req.query.errormsg, redirected: req.query.redirected});
//         });
// });

app.get('/getTime', async function (req, res) {
    var count = req.query.numGets
    var promises= []
    var start = Date.now();
    while(count>0){   
       promises.push(grpcGetRequestTest("akshay"+count))
        count-=1
    }
    Promise.all(promises).then((values) => {
        result = {}
        successRequests = 0
        failureRequests= 0
        for(data in values){
            if(!data.errormsg){
                successRequests+=1
            }
            else{
                failureRequests+=1
            }
        }
        var end = Date.now();
        result['successRequests'] = successRequests
        result['failureRequests'] = failureRequests
        result['totalOperationTime'] = (end- start)/1000
        res.json(result)

    });
    
});

app.get('/putTime', async function (req, res) {
    var count = req.query.numPuts
    var promises= []
    var start = Date.now();
    while(count>0){   
       promises.push(grpcPutRequest("akshay"+count, "awesome"+count))
        count-=1
    }
    Promise.all(promises).then((values) => {
        result = {}
        successRequests = 0
        failureRequests= 0
        for(data in values){
            if(!data.errormsg){
                successRequests+=1
            }
            else{
                failureRequests+=1
            }
        }
        var end = Date.now();
        result['successRequests'] = successRequests
        result['failureRequests'] = failureRequests
        result['totalOperationTime'] = (end-start)/1000
        res.json(result)
    });
});

//Set express app properties
app.set('port', process.env.PORT || 8000);

var server = app.listen(app.get('port'),async function () {
    console.log('server up and running' + server.address().port);
    //setInterval(receiveGrpcData, 5000);
});



function receiveRingData() {
    return new Promise((resolve, reject) => grpcClient.GetRing({}, function(err, response) {
        if(err) {
            console.log(err)
            resolve({"ring": [], errormsg: "Server down", role: "Unknown", entries: []})
        }
        resolve(response)        
    }))
}

function grpcPutRequest(key, value) {
    return new Promise((resolve, reject) => grpcClient.Put({key: key, value: value }, function(err, response){
        if(err) {
            console.log(err)
            resolve({"KVpairs": [], errormsg: "Server down"})
        }
        resolve(response)        
    }))
} 


function grpcGetRequest(key, value) {
    return new Promise((resolve, reject) => grpcClient.Get({key: key}, function(err, response){
        if(err) {
            resolve({"value": "", errormsg: "Server down"})
            }
            resolve(response)        
    }))

} 
