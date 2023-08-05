describe("Projection.Mercator", function() {
	var p = L.Projection.Mercator;

	expect.Assertion.prototype.near = function(expected, delta) {
		delta = delta || 1;
		expect(this.obj.x).to
			.be.within(expected.x - delta, expected.x + delta);
		expect(this.obj.y).to
			.be.within(expected.y - delta, expected.y + delta);
	};

	describe("#project", function() {
		it("projects a center point", function() {
			//edge cases
			expect(p.project(new L.LatLng(0, 0))).near(new L.Point(0, 0));
		});

		it("projects the northeast corner of the world", function() {
			expect(p.project(new L.LatLng(90, 180))).near(new L.Point(20037508, 20037508));
		});

		it("projects the southwest corner of the world", function() {
			expect(p.project(new L.LatLng(-90, -180))).near(new L.Point(-20037508, -20037508));
		});

		it("projects other points", function() {
			 expect(p.project(new L.LatLng(50, 30))).near(new L.Point(3339584, 6413524));

			 // from https://github.com/Leaflet/Leaflet/issues/1578
			 expect(p.project(new L.LatLng(51.9371170300465, 80.11230468750001)))
			 		.near(new L.Point(8918060.964088084, 6755099.410887127));
		});
	});

	describe("#unproject", function() {
		function pr(point) {
			return p.project(p.unproject(point));
		}

		it("unprojects a center point", function() {
			expect(pr(new L.Point(0, 0))).near(new L.Point(0, 0));
		});

		it("unprojects pi points", function() {
			expect(pr(new L.Point(-Math.PI, Math.PI))).near(new L.Point(-Math.PI, Math.PI));
			expect(pr(new L.Point(-Math.PI, -Math.PI))).near(new L.Point(-Math.PI, -Math.PI));

			expect(pr(new L.Point(0.523598775598, 1.010683188683))).near(new L.Point(0.523598775598, 1.010683188683));
		});

		it('unprojects other points', function () {
			// from https://github.com/Leaflet/Leaflet/issues/1578
			expect(pr(new L.Point(8918060.964088084, 6755099.410887127)));
		});
	});
});
