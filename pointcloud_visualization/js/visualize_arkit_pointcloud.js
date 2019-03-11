var camera, scene, renderer, controls;
var parameters;

var objects = [];
var materials = [];

var raycaster;

var moveForward = false;
var moveBackward = false;
var moveLeft = false;
var moveRight = false;
var canJump = false;

var prevTime = performance.now();
var velocity = new THREE.Vector3();
var direction = new THREE.Vector3();
var vertex = new THREE.Vector3();
var color = new THREE.Color();

var dataset = []

// Load the data
d3.csv("../data/arkit_pointcloud_upstairs.csv", (d) => {
    return {
        id: +d.id, // + cast as integer
        x: +d.x,
        y: +d.y,
        z: +d.z
    }
}, (data) => {
dataset = data;
    console.log("Dataset: " + dataset[0])
    init();
    animate();

});

function init() {

    camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 1000 );

    scene = new THREE.Scene();
    //scene.background = new THREE.Color( 0x6c91bf );
    scene.background = new THREE.Color( 0x524686 );
    scene.fog = new THREE.Fog( 0xffffff, 0, 750 );

    var light = new THREE.HemisphereLight( 0xeeeeff, 0x777788, 0.75 );
    light.position.set( 0.5, 1, 0.75 );
    scene.add( light );

    controls = new THREE.PointerLockControls( camera );

    var blocker = document.getElementById( 'blocker' );
    var instructions = document.getElementById( 'instructions' );

    instructions.addEventListener( 'click', function () {

        controls.lock();

    }, false );

    controls.addEventListener( 'lock', function () {

        instructions.style.display = 'none';
        blocker.style.display = 'none';

    } );

    controls.addEventListener( 'unlock', function () {

        blocker.style.display = 'block';
        instructions.style.display = '';

    } );

    scene.add( controls.getObject() );

    var onKeyDown = function ( event ) {

        switch ( event.keyCode ) {

            case 38: // up
            case 87: // w
                moveForward = true;
                break;

            case 37: // left
            case 65: // a
                moveLeft = true;
                break;

            case 40: // down
            case 83: // s
                moveBackward = true;
                break;

            case 39: // right
            case 68: // d
                moveRight = true;
                break;

            case 32: // space
                if ( canJump === true ) velocity.y += 350;
                canJump = false;
                break;

        }

    };

    var onKeyUp = function ( event ) {

        switch ( event.keyCode ) {

            case 38: // up
            case 87: // w
                moveForward = false;
                break;

            case 37: // left
            case 65: // a
                moveLeft = false;
                break;

            case 40: // down
            case 83: // s
                moveBackward = false;
                break;

            case 39: // right
            case 68: // d
                moveRight = false;
                break;

        }

    };

    document.addEventListener( 'keydown', onKeyDown, false );
    document.addEventListener( 'keyup', onKeyUp, false );

    raycaster = new THREE.Raycaster( new THREE.Vector3(), new THREE.Vector3( 0, - 1, 0 ), 0, 10 );

    // objects

    pointGeometry = new THREE.BufferGeometry();
    console.log("Dataset length: " + dataset.length);
    console.log("Dataset item 0: " + dataset[0]);

    var min_height = 0;
    var max_height = 0;

    for (i = 0; i < dataset.length; i++) {
        if (dataset[i]["z"] < min_height) {
            min_height = dataset[i]["z"];
        }
        if (dataset[i]["z"] > max_height) {
            max_height = dataset[i]["z"];
        }
    }

    console.log("Floor height:" + min_height);
    var pointArray = [];
    var colorArray = [];
    var n = 1000, n2 = n / 2;

    for (i = 0; i < dataset.length; i++) {

            // Space apart ARKit points appropriately into new environment
            var x = dataset[i]["x"] * 50;
            var y = dataset[i]["y"] * 50;
            var z = dataset[i]["z"] * 50;
            pointArray.push(x,y,z);

            var pointColor = new THREE.Color();

            // Build gradient pointcloud colors based on height in Y dimension
            var x = dataset[i]["y"]*(min_height/(min_height+max_height)) * n - n2;
            var y = dataset[i]["y"]*(min_height/(min_height+max_height)) * n - n2;
            var z = dataset[i]["y"]*(min_height/(min_height+max_height)) * n - n2;

            var vx = ( z / n ) + 0.65;
            var vy = ( 1 / n ) + 0.65 ;
            var vz = ( z / n ) + 0.65;

            colorArray.push(vx, vy, vz);
    }

    pointGeometry.addAttribute( 'position', new THREE.Float32BufferAttribute( pointArray, 3 ) );
    pointGeometry.addAttribute( 'color', new THREE.Float32BufferAttribute( colorArray, 3 ) );
    pointGeometry.computeBoundingSphere();

    var pointMaterial = new THREE.PointsMaterial( { size: 1, vertexColors: THREE.VertexColors } );
    points = new THREE.Points( pointGeometry, pointMaterial );
    scene.add( points );

    var bbox = new THREE.BoxHelper(points, 0xaf2bbf);
    bbox.update();
    scene.add(bbox);

    // floor

    var floorGeometry = new THREE.PlaneBufferGeometry( 2000, 2000, 100, 100 );
    floorGeometry.rotateX( - Math.PI / 2 );

    // vertex displacement

    var position = floorGeometry.attributes.position;

    for ( var i = 0, l = position.count; i < l; i ++ ) {

        vertex.fromBufferAttribute( position, i );

        vertex.x += Math.random() * 20 - 10;
        vertex.y += Math.random() * 2 - 200;
        vertex.z += Math.random() * 20 - 10;

        position.setXYZ( i, vertex.x, vertex.y, vertex.z );

    }

    floorGeometry = floorGeometry.toNonIndexed(); // ensure each face has unique vertices

    position = floorGeometry.attributes.position;
    var colors = [];

    for ( var i = 0, l = position.count; i < l; i ++ ) {

        color.setHSL( Math.random() * 0.3 + 0.5, 0.75, Math.random() * 0.25 + 0.75 );
        colors.push( color.r, color.g, color.b );

    }

    floorGeometry.addAttribute( 'color', new THREE.Float32BufferAttribute( colors, 3 ) );

    var floorMaterial = new THREE.MeshBasicMaterial( { vertexColors: THREE.VertexColors } );

    var floor = new THREE.Mesh( floorGeometry, floorMaterial );
    // scene.add( floor );

    //

    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );

    //

    window.addEventListener( 'resize', onWindowResize, false );

}

function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

    requestAnimationFrame( animate );

    if ( controls.isLocked === true ) {

        raycaster.ray.origin.copy( controls.getObject().position );
        raycaster.ray.origin.y -= 10;

        var intersections = raycaster.intersectObjects( objects );

        var onObject = intersections.length > 0;

        var time = performance.now();
        var delta = ( time - prevTime ) / 1000;

        velocity.x -= velocity.x * 10.0 * delta;
        velocity.z -= velocity.z * 10.0 * delta;

        velocity.y -= 9.8 * 100.0 * delta; // 100.0 = mass

        direction.z = Number( moveForward ) - Number( moveBackward );
        direction.x = Number( moveLeft ) - Number( moveRight );
        direction.normalize(); // this ensures consistent movements in all directions

        if ( moveForward || moveBackward ) velocity.z -= direction.z * 800.0 * delta;
        if ( moveLeft || moveRight ) velocity.x -= direction.x * 800.0 * delta;

        if ( onObject === true ) {

            velocity.y = Math.max( 0, velocity.y );
            canJump = true;

        }

        controls.getObject().translateX( velocity.x * delta );
        controls.getObject().translateY( velocity.y * delta );
        controls.getObject().translateZ( velocity.z * delta );

        if ( controls.getObject().position.y < 10 ) {

            velocity.y = 0;
            controls.getObject().position.y = 10;

            canJump = true;

        }

        prevTime = time;

    }

var time = Date.now() * 0.00005;

for (i = 0; i < scene.children.length; i++) {

    var object = scene.children[i];

    if (object instanceof THREE.PointCloud) {

        object.rotation.y = time * (i < 4 ? i + 1 : -(i + 1));
    }
}

for (i = 0; i < materials.length; i++) {

    color = parameters[i][0];

    h = (360 * (color[0] + time) % 360) / 360;
    materials[i].color.setHSL(h, color[1], color[2]);
}

renderer.render( scene, camera );

}

