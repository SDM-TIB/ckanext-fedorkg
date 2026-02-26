document.addEventListener('DOMContentLoaded', function () {
    const yasgui = new Yasgui(document.getElementById("yasgui"), {
        persistenceId: null,
        yasqe: {
            // modify codemirror tab handling to solely use 2 spaces
            tabSize: 2,
            indentUnit: 2,
            // set default query
            value: "SELECT DISTINCT ?concept\nWHERE {\n\t?s a ?concept\n} LIMIT 10"
        },
        extraKeys: {
            Tab: function (cm) {
                var spaces = new Array(cm.getOption("indentUnit") + 1).join(" ");
                cm.replaceSelection(spaces);
            }
        },
        requestConfig: {
            // configuring the endpoint for DeTrusty
            endpoint: sparql_url,
            method: "POST",
            args: [{name: "yasqe", value: true}]
        }
    });

    function attachQueryResponseHook(tab) {
        tab.yasqe.on('queryResponse', function (yasqe, req, duration) {
            tab.yasr.rootEl.style.display = '';
            try {
                let body = JSON.parse(req.text);
                if (body.error) {
                    flashError(body.error);
                    tab.yasr.rootEl.style.display = 'none';
                }
            } catch (e) {
                // Not JSON or not parseable — let YASGUI handle it normally
            }
        });
    }

    let tab = yasgui.getTab();
    tab.setName(default_query_name);
    tab.setQuery(default_query);
    attachQueryResponseHook(tab);
    tab.yasr.rootEl.style.display = 'none';

    yasgui.on('tabAdd', function (yasgui, tabId) {
        setTimeout(function () {
            let newTab = yasgui.getTab(tabId);
            if (newTab) {
                attachQueryResponseHook(newTab);
                newTab.yasr.rootEl.style.display = 'none';
            }
        }, 0);
    });

    const llm_form = document.getElementById("llm"),
          loader = document.querySelector("#loading");

    function displayLoading() {
        loader.classList.add("display");
    }

    function hideLoading() {
        loader.classList.remove("display");
    }

    function flashError(message) {
        let container = document.querySelector('.flash-messages');
        if (!container) return;

        let alertEl = document.createElement('div');
        alertEl.className = 'alert alert-dismissible fade show alert-danger';

        let btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-close close';
        btn.setAttribute('data-bs-dismiss', 'alert');
        btn.setAttribute('aria-label', 'Close');

        let text = document.createTextNode(message);

        alertEl.appendChild(text);
        alertEl.appendChild(btn);

        container.appendChild(alertEl);
    }

    llm_form.onsubmit = async function (event) {
        event.preventDefault();
        displayLoading();

        let data = new FormData();
        data.append("question", document.getElementById("question").value)

        try {
            const res = await fetch(llm_url, {method: "POST", body: data});
            hideLoading();

            if (!res.ok) {
                const body = await res.json();
                flashError(body.error || "An unexpected error occurred.");
                return;
            }

            const query = await res.text();
            tab = yasgui.getTab();
            tab.setName("LLM Query");
            tab.setQuery(query);
            tab.query();
        } catch (err) {
            hideLoading();
            flashError("An unexpected error occurred.");
            console.error(err);
        }
    };

    const question_elem = document.getElementById("question"),
          submit_btn = document.getElementById("llm_submit"),
          questions = document.querySelectorAll('.question');

    function handleClick(question) {
        question_elem.value = question;
        submit_btn.click();
    }

    questions.forEach(function(element) {
        element.addEventListener('click', function() {
            handleClick(element.textContent || element.innerText);
        });
    });
});
