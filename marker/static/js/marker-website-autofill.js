(() => {
	const DEBOUNCE_MS = 500;
	const MANAGED_FIELDS = [
		"name",
		"street",
		"postcode",
		"city",
		"country",
		"subdivision",
		"NIP",
		"REGON",
		"KRS",
		"court",
	];

	function getField(form, name) {
		const field = form?.elements?.namedItem(name);
		if (!field) {
			return null;
		}
		return Array.isArray(field) ? field[0] : field;
	}

	async function refreshSubdivision(form, subdivisionUrl, countryValue, subdivisionValue) {
		const subdivision = getField(form, "subdivision");
		if (!subdivision) {
			return;
		}

		if (!subdivisionUrl) {
			subdivision.value = subdivisionValue || "";
			return;
		}

		const url = new URL(subdivisionUrl, window.location.origin);
		url.searchParams.set("country", countryValue || "");

		try {
			const response = await fetch(url.toString(), {
				headers: { "X-Requested-With": "XMLHttpRequest" },
			});
			if (!response.ok) {
				return;
			}
			const html = await response.text();
			subdivision.innerHTML = html;
			subdivision.value = subdivisionValue || "";
		} catch {
			subdivision.value = subdivisionValue || "";
		}
	}

	function setManagedFields(form, fields) {
		const countryField = getField(form, "country");
		if (countryField) {
			countryField.value = fields.country || "";
		}

		for (const name of MANAGED_FIELDS) {
			if (name === "country" || name === "subdivision") {
				continue;
			}
			const field = getField(form, name);
			if (!field) {
				continue;
			}
			field.value = fields[name] || "";
		}
	}

	async function setupInput(input) {
		const form = input.form;
		if (!form) {
			return;
		}

		const autofillUrl = input.dataset.websiteAutofillUrl;
		const subdivisionUrl = input.dataset.subdivisionUrl;
		if (!autofillUrl) {
			return;
		}

		let timerId = null;
		let requestId = 0;

		const runAutofill = async () => {
			requestId += 1;
			const currentRequestId = requestId;

			const website = (input.value || "").trim();
			if (!website) {
				setManagedFields(form, {});
				await refreshSubdivision(form, subdivisionUrl, "", "");
				return;
			}

			const url = new URL(autofillUrl, window.location.origin);
			url.searchParams.set("website", website);

			let payload = null;
			try {
				const response = await fetch(url.toString(), {
					headers: {
						Accept: "application/json",
						"X-Requested-With": "XMLHttpRequest",
					},
				});
				if (!response.ok) {
					return;
				}
				payload = await response.json();
			} catch {
				return;
			}

			if (currentRequestId !== requestId) {
				return;
			}

			const fields = payload?.fields || {};
			setManagedFields(form, fields);
			await refreshSubdivision(
				form,
				subdivisionUrl,
				fields.country || "",
				fields.subdivision || ""
			);
		};

		const scheduleAutofill = () => {
			if (timerId) {
				clearTimeout(timerId);
			}
			timerId = window.setTimeout(() => {
				timerId = null;
				void runAutofill();
			}, DEBOUNCE_MS);
		};

		input.addEventListener("input", scheduleAutofill);
		input.addEventListener("change", () => {
			if (timerId) {
				clearTimeout(timerId);
				timerId = null;
			}
			void runAutofill();
		});
	}

	document.addEventListener("DOMContentLoaded", () => {
		const websiteInputs = document.querySelectorAll("input[data-website-autofill-url]");
		for (const input of websiteInputs) {
			void setupInput(input);
		}
	});
})();
