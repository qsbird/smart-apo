// Smart Awa + Smart Underwater Rev.A — authoritative parametric geometry
// Units: millimetres.  STL files in this package were independently generated
// and watertight-checked.  Use $fn=128 for final export.
$fn = 96;

part = "awa_body"; // awa_body, awa_cap, awa_sled, uw_A, uw_B, uw_ballast, flexure

awa_d = 32;
awa_h = 49;
awa_split_z = 15;
awa_wall = 1.4;
pcb_w = 12;
pcb_l = 35;
uw_d = 20;
uw_total_l = 70;
uw_straight_l = 50;

module ellipsoid(rx, ry, rz) { scale([rx,ry,rz]) sphere(1); }

module awa_outer() { ellipsoid(awa_d/2, awa_d/2, awa_h/2); }

module awa_body() {
  difference() {
    intersection() { awa_outer(); translate([-25,-25,-35]) cube([50,50,50]); }
    intersection() {
      translate([0,0,0.2]) ellipsoid(14.6,14.6,22.8);
      translate([-20,-20,-25]) cube([40,40,45]);
    }
    cylinder(h=60,r=0.75,center=true);                    // 316L wire/eye spine
    translate([12,0,-7.5]) rotate([0,90,0]) cylinder(h=12,r=1.65,center=true); // pressure port
  }
}

module awa_cap() {
  difference() {
    union() {
      intersection() { awa_outer(); translate([-25,-25,10]) cube([50,50,20]); }
      difference() {
        translate([0,0,14]) cylinder(h=4,r=11.55,center=true);
        translate([0,0,14]) cylinder(h=6,r=9.55,center=true);
      }
    }
    intersection() {
      translate([0,0,0.2]) ellipsoid(14.6,14.6,22.8);
      translate([-20,-20,7.5]) cube([40,40,16]);
    }
    cylinder(h=35,r=0.75,center=true);
    translate([5.8,0,19]) cylinder(h=20,r=1.55,center=true); // light pipe
    for (x=[-5,-2.8,-0.6,1.6]) translate([x,-2.1,19]) cylinder(h=20,r=0.65,center=true);
  }
}

module awa_sled() {
  union() {
    translate([-4.2,0,-1.5]) cube([12.6,1,35.6],center=true);
    translate([-10,0.7,-1.5]) cube([1,2.4,35.6],center=true);
    translate([1.6,0.7,-1.5]) cube([1,2.4,35.6],center=true);
    translate([5.8,0,-3.5]) cube([9.5,1,30],center=true);
  }
}

module capsule(r=10, straight=50) {
  union() {
    cylinder(h=straight,r=r,center=true);
    translate([0,0,straight/2]) sphere(r);
    translate([0,0,-straight/2]) sphere(r);
  }
}

module uw_shell() {
  difference() {
    union() {
      capsule(uw_d/2,uw_straight_l);
      for (x=[-7.2,7.2], z=[-17,17])
        translate([x,0,z]) rotate([90,0,0]) cylinder(h=24,r=2.6,center=true);
    }
    cube([13.2,8,43],center=true);                         // electronics cavity
    cube([7,1,76],center=true);                            // 316L beam slot
    translate([8,0,-7]) rotate([0,90,0]) cylinder(h=10,r=1.65,center=true);
    for (x=[-7.2,7.2], z=[-17,17])
      translate([x,0,z]) rotate([90,0,0]) cylinder(h=28,r=1.1,center=true);
  }
}

module uw_half(sign=1) {
  intersection() {
    uw_shell();
    translate([0,sign*25.01,0]) cube([50,50,90],center=true);
  }
}

module uw_ballast() {
  translate([0,0,-14]) difference() {
    cube([9,5.5,12],center=true);
    translate([0,0,0.8]) cube([7.2,4,10.5],center=true);
  }
}

module flexure_316L() {
  // Preview only. Manufacture from the DXF in 0.30 mm 316L sheet.
  difference() {
    linear_extrude(0.30) polygon([
      [-4,-39],[4,-39],[4,-29],[2.5,-24],[1.2,-18],[0.75,-11],
      [0.75,11],[1.2,18],[2.5,24],[4,29],[4,39],[-4,39],
      [-4,29],[-2.5,24],[-1.2,18],[-0.75,11],[-0.75,-11],
      [-1.2,-18],[-2.5,-24],[-4,-29]
    ]);
    for (y=[-33.5,33.5]) translate([0,y,-0.2]) cylinder(h=1,r=1.6);
  }
}

if (part=="awa_body") awa_body();
else if (part=="awa_cap") awa_cap();
else if (part=="awa_sled") awa_sled();
else if (part=="uw_A") uw_half(-1);
else if (part=="uw_B") uw_half(1);
else if (part=="uw_ballast") uw_ballast();
else if (part=="flexure") flexure_316L();

