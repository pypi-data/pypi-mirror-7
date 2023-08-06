/*-------------------------------google map function start-------------------------------*/

var map;
var marker;
var infowindow;
var geocoder;
var circle_markers = [];
var markers = [];
var id_address;
var id_lng;
var id_lat;
var draggable = false;
var resizable = false;
var mouseX, mouseY, drawnX, drawnY, diffX, diffY;
var has_typecontrol = false;

function initializeMap(map_tid, address_tid, lng_tid, lat_tid, marker_name, is_resize, is_offset) {
    var latlng = new google.maps.LatLng(0, 0);
    var myOptions = {
        zoom: 2,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false,
        draggable: true,
        scrollwheel: true
    };
    map = new google.maps.Map(document.getElementById(map_tid), myOptions);

    geocoder = new google.maps.Geocoder();

    //Listener mouse event of right click
    google.maps.event.addListener(map, "click", function (event) {
        placeMarker(event.latLng);
    });

    google.maps.event.addListenerOnce(map, "tilesloaded", function () {
        //Init marker
        addMarker(marker_name);
        initMarker(address_tid, lng_tid, lat_tid);
        initSearch();
        if(is_resize) initResize();
        if(is_offset) initOffset();
    });
}

function initSearch() {
    var search = document.createElement("input");
    search.id = "map_search";
    search.type = "text";
    search.style.marginTop = "5px";

    var node = $(map.getDiv());
    var width = node.width() ? node.width() : 500;
    if (width < 400) {
        search.style.display = "none";
    }

    map.controls[google.maps.ControlPosition.TOP_CENTER].push(search);
    var searchBox = new google.maps.places.SearchBox(search);
    var _markers = [];

    google.maps.event.addListener(searchBox, 'places_changed', function () {
        var places = searchBox.getPlaces();

        clearOverlays(_markers);

        var bounds = new google.maps.LatLngBounds();
        for (var i = 0, place; place = places[i]; i++) {
            var image = {
                url: place.icon,
                size: new google.maps.Size(71, 71),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(17, 34),
                scaledSize: new google.maps.Size(25, 25)
            };

            var _marker = new google.maps.Marker({
                map: map,
                icon: image,
                title: place.name,
                position: place.geometry.location
            });

            google.maps.event.addListener(_marker, 'click', function (event) {
                clearOverlays(_markers);
                placeMarker(event.latLng);
            });

            _markers.push(_marker);

            bounds.extend(place.geometry.location);
        }

        map.fitBounds(bounds);
    });

    google.maps.event.addListener(map, 'bounds_changed', function () {
        var bounds = map.getBounds();
        searchBox.setBounds(bounds);
    });
}

function initMarker(address_tid, lng_tid, lat_tid) {
    id_address = address_tid;
    id_lng = lng_tid;
    id_lat = lat_tid;
    var address = document.getElementById(id_address).value;
    var lng = document.getElementById(id_lng).value;
    var lat = document.getElementById(id_lat).value;

    if (lng != 0 || lat != 0) {
        var latlng = new google.maps.LatLng(lat, lng);

//        var circle = new google.maps.Circle({
//            strokeColor: "#86ACDE",
//            strokeOpacity: 0.8,
//            strokeWeight: 2,
//            fillColor: "#DCE2EA",
//            fillOpacity: 0.7,
//            map: map,
//            center: latlng,
//            radius: 5000
//        });

        marker = new google.maps.Marker({
            icon: "/static/img/marker_circle.png",
            position: latlng,
            map: map
        });
        circle_markers.push(marker);
        if (!address) {
            getAddress(new google.maps.LatLng(lat, lng), address);
        } else {
            attachSecretMessage(marker, latlng, address);
        }
    }else if(address){
        geocoder.geocode({'address': address}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                var location = results[0].geometry.location;
                marker = new google.maps.Marker({
                    icon: "/static/img/marker_circle.png",
                    position: results[0].geometry.location,
                    map: map
                });
                circle_markers.push(marker);
                attachSecretMessage(marker, location, address);
            } else {
                //alert("Unable to resolve the address of the reasons: " + status);
            }
        });
    }
}

function addMarker(marker_name) {
    if (marker_name) {
        var marker_list = document.getElementsByName(marker_name);
        for (var i = 0; i < marker_list.length; i++) {
            var location = marker_list[i].value.split(",");
            var link = marker_list[i].getAttribute('data-link');
            var latlng = new google.maps.LatLng(location[1], location[0]);
            marker = new google.maps.Marker({
                icon: "/static/img/marker_green.png",
                position: latlng,
                map: map,
                link: link
                //icon: "http://maps.google.com/mapfiles/marker_green.png"
            });

            markers.push(marker);

//            google.maps.event.addListener(marker, 'click', function (event) {
//                clearOverlays(marker);
//                placeMarker(event.latLng);
//            });

            google.maps.event.addListener(marker, 'click', function (event) {
                if(this.link){
                    $.colorbox({
                        href: link,
                        fastIframe: false,
                        opacity: 0.6
                    });
                }else{
                    clearOverlays(marker);
                    placeMarker(event.latLng);
                }
            });
        }
    }
}

function placeMarker(location) {
    //Clear all marker
    clearOverlays(circle_markers, infowindow);
    marker = new google.maps.Marker({
        icon: "/static/img/marker_circle.png",
        position: location,
        map: map
    });
    circle_markers.push(marker);
    //Get address by location
    getAddress(location);
}

function getAddress(location, address) {
    if (geocoder) {
        geocoder.geocode({ 'location': location }, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                if (results[0]) {
                    location = results[0].geometry.location;
                    if (!address) {
                        address = results[0].formatted_address;
                    }
                    attachSecretMessage(marker, location, address);
                }
            } else {
                attachSecretMessage(marker, location, "Unknown");
                console.log("Geocoder failed due to: " + status);
            }
        });
    }
}

function attachSecretMessage(marker, piont, address) {
    map.panTo(piont);
    //var message = "<b>Position: </b>" + piont.lat() + " , " + piont.lng() + "<br />" + "<b>Address: </b>" + address;
    var message = "<b>Address: </b>" + address;
    var infowindow = new google.maps.InfoWindow(
        {
            content: message,
            disableAutoPan: true,
            maxWidth: 300
        });
    infowindow.open(map, marker);
    if (typeof (mapClick) == "function") mapClick(piont.lng(), piont.lat(), address == "Unknown" ? "" : address);
}

function clearOverlays(obj, infowindow) {
    if (obj && obj.length > 0) {
        for (var i = 0; i < obj.length; i++) {
            obj[i].setMap(null);
        }
        obj.length = 0;
        obj = [];
    }
    if (infowindow) {
        infowindow.close();
    }
}

function mapClick(lng, lat, address) {
    document.getElementById(id_lng).value = lng;
    document.getElementById(id_lat).value = lat;
    document.getElementById(id_address).value = address;
}

function initResize() {
    var drag = document.createElement("div");
    drag.className = "drag";
    drag.onmousedown = function () {
        resizable = true;
    };
    drag.onmouseup = function () {
        resizable = false;
    };
    var node = map.getDiv();
    var childNodes = node.firstChild.childNodes;
    node.appendChild(drag);
    //node.firstChild.childNodes[5].style.marginRight = "25px";
    //cleanTerms(1000);

    google.maps.event.addDomListener(window, 'mousemove', function () {
        watchMouse();
    });
}

function initOffset() {
    $("#btn_offset").on("click", function(){
        var offset = $("#id_offset").val();
        if(offset){
            $.each(markers, function(key, item){
                var lat = parseFloat(item.getPosition().lat());
                var lng = parseFloat(item.getPosition().lng());
                var rn = random_num(-offset, offset);
                lat = lat + rn;
                lng = lng + rn;
                item.setPosition(new google.maps.LatLng(lat, lng));
            });
        }
    });
}

function random_num(min, max) {
    return parseInt(Math.random() * (max - min + 1) + min);
}

/*function find_num(array, sum) {
    if (array && array.length > 0) {
        var begin = 0;
        var end = array.length - 1;

        while (begin < end) {
            var current_sum = Math.pow(array[begin], 2) + Math.pow(array[end], 2);
            if (current_sum < sum) {
                begin++;
            } else if (current_sum > sum) {
                end--;
            } else {
                console.log(array[begin] + "   " + array[end]);
                begin++;
                end--;
            }
        }
    }
}*/

function cleanTerms(delay){
    var node = map.getDiv();
    var childNodes = node.firstChild.childNodes;
    setInterval(function(){
        for (var i = 0; i < childNodes.length; i++) {
            if(childNodes[i].style.right == "0px" && childNodes[i].style.bottom == "0px"){
                childNodes[i].remove();
            }
        }
    }, delay ? delay : 1000);
}

function watchMouse(e) {
    var left = window.scrollX || document.documentElement.scrollLeft || 0;
    var top = window.scrollY || document.documentElement.scrollTop || 0;
    if (!e) e = window.event;
    mouseX = e.clientX + left;
    mouseY = e.clientY + top;
    var offsetWidth = mouseX - diffX;
    var offsetHeight = mouseY - diffY;
    diffX = mouseX;
    diffY = mouseY;
    if (resizable) {
        changeMapSize(offsetWidth, offsetHeight);
    } else if (draggable) {
        map.getDiv().style.left = (mouseX - drawnX) + "px";
        map.getDiv().style.top = (mouseY - drawnY) + "px";
    }
    return false;
}

function changeMapSize(offsetWidth, offsetHeight) {
    var node = map.getDiv().style;
    var width = parseInt(node.width ? node.width : 500);
    var height = parseInt(node.height ? node.height : 400);
    var search = document.getElementById("map_search")
    if (width < 100 || height < 100) {
        resizable = false;
        width += 100;
        height += 100;
    }
    if (width > 400 && !has_typecontrol) {
        has_typecontrol = true;
        map.setOptions({
            mapTypeControl: true
        });
        if (search.style.display == "none") {
            search.style.width = "120px";
            search.style.display = "block";
        }
    } else if (width < 400 && has_typecontrol) {
        has_typecontrol = false;
        map.setOptions({
            mapTypeControl: false
        });
    }
    node.width = (width + offsetWidth) + "px";
    node.height = (height + offsetHeight) + "px";
    if (search) {
        var search_width = 220;
        if (search.style.width.indexOf("px") != -1) {
            search_width = parseInt(search.style.width.split("px")[0])
        }
        if (search_width < 50) {
            search.style.display = "none";
        } else {
            search_width += offsetWidth;
            search.style.width = search_width + "px";
        }
    }
    google.maps.event.trigger(map, "resize");
}

$(function(){
    $("form:first").submit(function () {
        if ($("#map_search").is(":focus")) {
            return false;
        }
    });

    $("#add_ip_form").submit(function () {
        var ip_string = $("#ip_string").val();
        if (ip_string) {
            $.ajax({
                url: "/googlemap/get_locations/",
                type: "POST",
                dataType: "json",
                data: {ip_string: ip_string},
                async: true,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                },
                success: function (data) {
                    if (data.status == "success") {
                        var locations = data.data;
                        $.each(locations, function (i, location) {
                            marker = new google.maps.Marker({
                                icon: "/static/img/marker_green.png",
                                position: location,
                                map: map
                            });
                            markers.push(marker);
                        });
                    }
                }
            });
        }
        return false;
    });
});

/*-------------------------------google map function end-------------------------------*/