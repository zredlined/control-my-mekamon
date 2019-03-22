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

var points_dataset = []
var planes_dataset = []

// Load the data
d3.queue()
.defer(d3.csv, "./data/spotmeka_points.csv")
.defer(d3.csv, "./data/spotmeka_anchors.csv")
.defer(d3.csv, "./data/spotmeka_camera.csv")
.defer(d3.csv, "./data/spotmeka_objects.csv")
.await(function(error, points_file, planes_file, camera_file, objects_file) {
    if (error) {
        console.error('Something went wrong: ' + error);
    }
    else {
        points_dataset = points_file;
        planes_dataset = planes_file;
        camera_dataset = camera_file;
        objects_dataset = objects_file;
        console.log("Points Dataset: " + points_dataset[0]);
        console.log("Planes Dataset: " + planes_dataset[0]);
        console.log("Camera Dataset: " + camera_dataset[0]);
        console.log("Objects Dataset: " + objects_dataset[0]);
        init();
        animate();
    }
});

function init() {

    camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 1000 );

    scene = new THREE.Scene();
    //scene.background = new THREE.Color( 0x6c91bf );
    //scene.fog = new THREE.Fog( 0xffffff, 0, 750 );
    scene.background = new THREE.Color( 0x1C1C1C );
    scene.fog = new THREE.Fog( 0xCCCCCC, 0, 750 );

    //var light = new THREE.HemisphereLight( 0xeeeeff, 0x777788, 0.75 );
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

    // Points

    pointGeometry = new THREE.BufferGeometry();
    var min_height = 0;
    var max_height = 0;

    for (i = 0; i < points_dataset.length; i++) {
        var current_height = points_dataset[i]["y"] * 50;

        if (current_height < min_height) {
            min_height = current_height;
        }
        if (current_height > max_height) {
            max_height = current_height;
        }
    }

    console.log("Floor height:" + min_height);
    var pointArray = [];
    var colorArray = [];
    var n = 1000, n2 = n / 2;

    console.log(min_height, max_height);
    for (i = 0; i < points_dataset.length; i++) {

            // Space apart ARKit points appropriately into new environment
            var x = points_dataset[i]["x"] * 50;
            var y = points_dataset[i]["y"] * 50;
            var z = points_dataset[i]["z"] * 50;
            pointArray.push(x,y,z);

            var pointColor = new THREE.Color();

            // Build gradient pointcloud colors based on height in Y dimension
            var delta = max_height - min_height;
            var red = ((y-min_height) / delta);
            var green = 1.0-((y-min_height) / delta);
            var blue = ((y-min_height) / delta);

            //colorArray.push(vx, 1.0, vz);
            colorArray.push(0.0, green, blue);
    }

    pointGeometry.addAttribute( 'position', new THREE.Float32BufferAttribute( pointArray, 3 ) );
    pointGeometry.addAttribute( 'color', new THREE.Float32BufferAttribute( colorArray, 3 ) );
    pointGeometry.computeBoundingSphere();

    var pointMaterial = new THREE.PointsMaterial( { size: 1, vertexColors: THREE.VertexColors, opacity:0.9, transparent:false } );
    points = new THREE.Points( pointGeometry, pointMaterial );
    scene.add( points );

    var bbox = new THREE.BoxHelper(points, 0x7a7978);
    bbox.update();
    scene.add(bbox);


    // anchors
    for (i = 0; i < planes_dataset.length; i++) {

        var pos_x = planes_dataset[i].pos_x * 50;
        var pos_y = planes_dataset[i].pos_y * 50;
        var pos_z = planes_dataset[i].pos_z * 50;
        var rot_w = planes_dataset[i].rot_w * 50;
        var rot_x = planes_dataset[i].rot_x * 50;
        var rot_y = planes_dataset[i].rot_y * 50;
        var rot_z = planes_dataset[i].rot_z * 50;
        var width = planes_dataset[i].width * 50;
        var length = planes_dataset[i].length * 50;

        let cube_height = 0.1;

        var geometry = new THREE.BoxGeometry( width, cube_height, length );
        var material = new THREE.MeshPhongMaterial({ color: 0x7a7978, opacity: 0.7, transparent: true });
        var cube = new THREE.Mesh(geometry, material);

        if (planes_dataset[i].orientation == "VerticalPlaneAnchor") {
            cube.rotateX( - Math.PI / 2); // use this to make vertical
        }

        //cube.rotateY(rot_x);

        scene.add(cube);
        cube.position.set(pos_x, pos_y, pos_z);
        // Set as quaternion vs Euler
        // https://threejs.org/docs/#api/en/math/Quaternion
        // cube.quaternion.set(rot_x, rot_y, rot_z, rot_w);
    }

    // objects
    for (i = 0; i < objects_dataset.length; i++) {

        var pos_x = objects_dataset[i].pos_x * 50;
        var pos_y = objects_dataset[i].pos_y * 50;
        var pos_z = objects_dataset[i].pos_z * 50;
        var width = objects_dataset[i].width * 50;
        var length = objects_dataset[i].length * 50;

        var geometry = new THREE.BoxGeometry( 10, 10, 10 );
        var material = new THREE.MeshPhongMaterial({ color: 0xEE0979, opacity: 0.8, transparent: true });
        var cube = new THREE.Mesh(geometry, material);

        scene.add(cube);
        cube.position.set(pos_x, pos_y, pos_z);
    }

    // camera path
    var camera_geometry = new THREE.Geometry();
    for (i = 0; i < camera_dataset.length; i++) {

        var pos_x = camera_dataset[i].x * 50;
        var pos_y = camera_dataset[i].y * 50;
        var pos_z = camera_dataset[i].z * 50;

        var xyz_point = new THREE.Vector3(pos_x, pos_y, pos_z);
        camera_geometry.vertices.push(xyz_point);
    }
    var camera_line = new MeshLine();
    camera_line.setGeometry( camera_geometry );
    var camera_material = new MeshLineMaterial();

    var camera_mesh = new THREE.Mesh( camera_line.geometry, camera_material );
    scene.add( camera_mesh );

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

