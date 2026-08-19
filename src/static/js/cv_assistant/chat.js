/**
 * CV Assistant Chat - vanilla JS frontend.
 * Uses Django session auth (cookie + CSRF token) for all API calls.
 */
(function () {
    'use strict';

    // ---- Config ----
    var API_BASE = '/api/v1/cv-assistant/';

    // ---- State ----
    var state = {
        jobs: [],
        selectedJobId: null,
        messages: [],
        cvVersions: [],
        recruiterResponses: [],
        csrfToken: null,
        sending: false
    };

    // ---- DOM helpers ----
    function $(id) { return document.getElementById(id); }
    function escapeHtml(str) {
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // ---- CSRF ----
    function getCSRFFromCookie() {
        var name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    return decodeURIComponent(cookie.substring(name.length + 1));
                }
            }
        }
        return null;
    }
    function getCSRFToken() {
        if (state.csrfToken) return state.csrfToken;
        var meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) {
            state.csrfToken = meta.getAttribute('content');
            return state.csrfToken;
        }
        state.csrfToken = getCSRFFromCookie();
        return state.csrfToken;
    }

    // ---- Fetch wrapper (session auth) ----
    function apiCall(method, path, body) {
        var headers = {
            'Accept': 'application/json'
        };
        var opts = { method: method, headers: headers, credentials: 'same-origin' };
        var csrf = getCSRFToken();
        if (csrf) headers['X-CSRFToken'] = csrf;
        if (body !== undefined && body !== null) {
            headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }
        return fetch(API_BASE + path, opts).then(function (resp) {
            if (resp.status === 204) return null;
            if (resp.status >= 400) {
                return resp.json().then(function (data) {
                    var err = new Error('API Error ' + resp.status);
                    err.data = data;
                    err.status = resp.status;
                    throw err;
                }, function () {
                    var err = new Error('API Error ' + resp.status);
                    err.status = resp.status;
                    throw err;
                });
            }
            return resp.json();
        });
    }

    // ---- Toast / inline errors ----
    function showError(msg) {
        var area = $('messages-area');
        var div = document.createElement('div');
        div.className = 'message role-system';
        div.textContent = 'Error: ' + (msg || 'unknown error');
        if (area) area.appendChild(div);
        if (area) area.scrollTop = area.scrollHeight;
    }

    // ---- Jobs list ----
    function loadJobs() {
        apiCall('GET', 'jobs/').then(function (data) {
            var results = data.results || data || [];
            state.jobs = results;
            renderJobsList();
        }).catch(function (err) {
            $('jobs-list').innerHTML = '<li class="jobs-empty">Failed to load applications</li>';
            console.error(err);
        });
    }

    function renderJobsList(filter) {
        var list = $('jobs-list');
        list.innerHTML = '';
        var filtered = state.jobs;
        if (filter) {
            filter = filter.toLowerCase();
            filtered = state.jobs.filter(function (j) {
                return (j.company || '').toLowerCase().indexOf(filter) !== -1 ||
                       (j.position || '').toLowerCase().indexOf(filter) !== -1;
            });
        }
        if (!filtered.length) {
            list.innerHTML = '<li class="jobs-empty">No applications found.</li>';
            return;
        }
        filtered.forEach(function (job) {
            var li = document.createElement('li');
            if (job.id === state.selectedJobId) li.classList.add('active');
            li.dataset.jobId = job.id;
            li.innerHTML = '<div class="job-company">' + escapeHtml(job.company || 'Unknown') + '</div>' +
                           '<div class="job-position">' + escapeHtml(job.position || '') + '</div>';
            li.addEventListener('click', function () { selectJob(job.id); });
            list.appendChild(li);
        });
    }

    // ---- Select a job -> load messages + CV versions ----
    function selectJob(jobId) {
        state.selectedJobId = jobId;
        renderJobsList($('job-search').value);
        var job = state.jobs.find(function (j) { return j.id === jobId; });
        if (!job) return;

        // Header
        $('selected-job-title').textContent = job.company + ' — ' + (job.position || '');
        var badge = $('selected-job-status');
        badge.textContent = job.status || '';
        badge.className = 'status-badge s-' + (job.status || 'draft');
        $('generate-cv-btn').disabled = false;
        $('mark-sent-btn').disabled = (job.status === 'sent');
        $('message-input').disabled = false;
        $('send-btn').disabled = false;
        $('recruiter-form').style.display = '';

        loadMessages(jobId);
        loadCVVersions(jobId);
        loadRecruiterResponses(jobId);
    }

    // ---- Messages ----
    function loadMessages(jobId) {
        apiCall('GET', 'jobs/' + jobId + '/messages/').then(function (data) {
            var results = data.results || data || [];
            state.messages = results;
            renderMessages();
        }).catch(function (err) {
            console.error(err);
            showError(err.message);
        });
    }

    function renderMessages() {
        var area = $('messages-area');
        area.innerHTML = '';
        if (!state.messages.length) {
            area.innerHTML = '<div class="chat-empty-state"><i class="fas fa-comments"></i>' +
                             '<p>No messages yet. Start the conversation!</p></div>';
            return;
        }
        state.messages.forEach(function (msg) {
            area.appendChild(renderMessage(msg));
        });
        area.scrollTop = area.scrollHeight;
    }

    function renderMessage(msg) {
        var div = document.createElement('div');
        var role = msg.role || 'user';
        div.className = 'message role-' + role;
        if (msg.content_html) {
            // Server-rendered HTML (markdown) for assistant/user messages.
            var body = document.createElement('div');
            body.className = 'msg-body';
            body.innerHTML = msg.content_html;
            div.appendChild(body);
        } else {
            div.textContent = msg.content || '';
        }
        var meta = document.createElement('div');
        meta.className = 'msg-meta';
        meta.textContent = role.charAt(0).toUpperCase() + role.slice(1);
        if (msg.created_at) {
            meta.textContent += ' · ' + new Date(msg.created_at).toLocaleString();
        }
        div.appendChild(meta);
        return div;
    }

    function sendMessage() {
        var input = $('message-input');
        var content = input.value.trim();
        if (!content || !state.selectedJobId || state.sending) return;
        state.sending = true;
        $('send-btn').disabled = true;

        // Optimistic render
        var area = $('messages-area');
        var placeholder = area.querySelector('.chat-empty-state');
        if (placeholder) area.innerHTML = '';
        var optimistic = renderMessage({ role: 'user', content: content, created_at: new Date().toISOString() });
        area.appendChild(optimistic);
        area.scrollTop = area.scrollHeight;

        input.value = '';

        // Loading indicator
        var loading = document.createElement('div');
        loading.className = 'chat-loading-dots';
        loading.textContent = 'AI is thinking';
        area.appendChild(loading);
        area.scrollTop = area.scrollHeight;

        apiCall('POST', 'jobs/' + state.selectedJobId + '/messages/', { content: content })
            .then(function (resp) {
                if (loading.parentNode) loading.parentNode.removeChild(loading);
                if (Array.isArray(resp) && resp.length > 0) {
                    // resp is [user_message, assistant_message]
                    // Replace optimistic with the real assistant reply
                    area.appendChild(renderMessage(resp[resp.length - 1]));
                }
                area.scrollTop = area.scrollHeight;
            })
            .catch(function (err) {
                if (loading.parentNode) loading.parentNode.removeChild(loading);
                showError(err.data ? JSON.stringify(err.data) : err.message);
            })
            .then(function () {
                state.sending = false;
                $('send-btn').disabled = false;
            });
    }

    // ---- Generate CV ----
    function generateCV() {
        if (!state.selectedJobId) return;
        var btn = $('generate-cv-btn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        apiCall('POST', 'jobs/' + state.selectedJobId + '/generate-cv/', {})
            .then(function (resp) {
                btn.innerHTML = '<i class="fas fa-check"></i> CV Generated';
                showSystemMessage('CV generated successfully.');
                loadCVVersions(state.selectedJobId);
                setTimeout(function () {
                    btn.innerHTML = '<i class="fas fa-file-alt"></i> Generate CV';
                    btn.disabled = false;
                }, 2000);
            })
            .catch(function (err) {
                btn.innerHTML = '<i class="fas fa-file-alt"></i> Generate CV';
                btn.disabled = false;
                showError(err.data ? JSON.stringify(err.data) : err.message);
            });
    }

    function showSystemMessage(text) {
        var area = $('messages-area');
        var div = document.createElement('div');
        div.className = 'message role-system';
        div.textContent = text;
        area.appendChild(div);
        area.scrollTop = area.scrollHeight;
    }

    // ---- Mark as Sent ----
    function markAsSent() {
        if (!state.selectedJobId) return;
        apiCall('PATCH', 'jobs/' + state.selectedJobId + '/', { status: 'sent' })
            .then(function (resp) {
                $('selected-job-status').textContent = 'sent';
                $('selected-job-status').className = 'status-badge s-sent';
                $('mark-sent-btn').disabled = true;
                showSystemMessage('Application marked as sent.');
                loadJobs();
            })
            .catch(function (err) {
                showError(err.data ? JSON.stringify(err.data) : err.message);
            });
    }

    // ---- CV Versions ----
    function loadCVVersions(jobId) {
        apiCall('GET', 'cv-versions/?job=' + jobId).then(function (data) {
            var results = data.results || data || [];
            state.cvVersions = results;
            renderCVVersions();
            populateRecruiterCVVersionSelect();
        }).catch(function (err) {
            console.error(err);
            $('cv-versions-list').innerHTML = '<li class="panel-empty">Failed to load CV versions.</li>';
        });
    }

    function renderCVVersions() {
        var list = $('cv-versions-list');
        if (!state.cvVersions.length) {
            list.innerHTML = '<li class="panel-empty">No CV versions yet.</li>';
            return;
        }
        list.innerHTML = state.cvVersions.map(function (v) {
            var pdf = v.pdf_file || v.pdf_url || '';
            if (pdf && pdf.indexOf('http') !== 0 && pdf.indexOf('/') !== 0) {
                pdf = '/' + pdf;
            }
            var link = pdf ? '<a href="' + escapeHtml(pdf) + '" target="_blank" class="cv-version-link"><i class="fas fa-file-pdf"></i> Download PDF</a>' : '';
            return '<li class="cv-version-item">' + link +
                '<span class="cv-version-meta">v' + escapeHtml(String(v.version_number || v.id)) +
                (v.created_at ? ' · ' + new Date(v.created_at).toLocaleDateString() : '') +
                '</span></li>';
        }).join('');
    }

    function populateRecruiterCVVersionSelect() {
        var select = $('recruiter-cv-version');
        if (!select) return;
        select.innerHTML = '<option value="">Select CV version...</option>';
        state.cvVersions.forEach(function (v) {
            var opt = document.createElement('option');
            opt.value = v.id;
            opt.textContent = 'v' + v.version_number;
            select.appendChild(opt);
        });
    }

    // ---- Recruiter responses ----
    function loadRecruiterResponses(jobId) {
        apiCall('GET', 'recruiter-responses/?job=' + jobId).then(function (data) {
            var results = data.results || data || [];
            state.recruiterResponses = results;
            renderRecruiterResponses();
        }).catch(function (err) {
            console.error(err);
            $('recruiter-responses-list').innerHTML = '<li class="panel-empty">Failed to load responses.</li>';
        });
    }

    function renderRecruiterResponses() {
        var list = $('recruiter-responses-list');
        if (!state.recruiterResponses.length) {
            list.innerHTML = '<li class="panel-empty">Nothing yet.</li>';
            return;
        }
        list.innerHTML = state.recruiterResponses.map(function (r) {
            return '<li><strong>' + escapeHtml(r.response_type || 'unknown') + '</strong>' +
                '<br>' + escapeHtml(r.notes || '') + '</li>';
        }).join('');
    }

    function submitRecruiterResponse(e) {
        e.preventDefault();
        var cvVersionId = $('recruiter-cv-version').value;
        if (!cvVersionId) return;
        apiCall('POST', 'recruiter-responses/', {
            cv_version: parseInt(cvVersionId, 10),
            response_type: $('recruiter-response-type').value,
            notes: $('recruiter-notes').value.trim(),
        }).then(function () {
            $('recruiter-notes').value = '';
            loadRecruiterResponses(state.selectedJobId);
        }).catch(function (err) {
            showError(err.data ? JSON.stringify(err.data) : err.message);
        });
    }

    // ---- New application ----
    function showNewJobModal() { $('new-job-modal').style.display = 'flex'; }
    function hideNewJobModal() { $('new-job-modal').style.display = 'none'; }

    function createNewJob(e) {
        e.preventDefault();
        var payload = {
            company: $('company').value.trim(),
            position: $('position').value.trim(),
            job_description: $('job-description').value.trim(),
        };
        if (!payload.company || !payload.position) return;
        apiCall('POST', 'jobs/', payload)
            .then(function (resp) {
                hideNewJobModal();
                $('new-job-form').reset();
                return loadJobs();
            })
            .then(function () {
                // select the newly created (most recent) job
                if (state.jobs.length) {
                    var newest = state.jobs[0];
                    selectJob(newest.id);
                }
            })
            .catch(function (err) {
                showError(err.data ? JSON.stringify(err.data) : err.message);
            });
    }

    // ---- Toggle right panel ----
    function togglePanel() {
        var panel = $('cv-panel');
        panel.classList.toggle('cv-panel-hidden');
    }

    // ---- Wire up events ----
    function init() {
        // Pre-fetch CSRF token (meta tag already set in template)
        getCSRFToken();

        $('new-job-btn').addEventListener('click', showNewJobModal);
        $('modal-cancel-btn').addEventListener('click', hideNewJobModal);
        $('new-job-form').addEventListener('submit', createNewJob);
        $('new-job-modal').addEventListener('click', function (e) {
            if (e.target === this) hideNewJobModal();
        });

        $('send-btn').addEventListener('click', sendMessage);
        $('message-input').addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        $('generate-cv-btn').addEventListener('click', generateCV);
        $('mark-sent-btn').addEventListener('click', markAsSent);
        $('toggle-panel-btn').addEventListener('click', togglePanel);
        $('close-panel-btn').addEventListener('click', togglePanel);

        $('recruiter-form').addEventListener('submit', submitRecruiterResponse);

        $('job-search').addEventListener('input', function () {
            renderJobsList(this.value);
        });

        // Initial load
        loadJobs();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();