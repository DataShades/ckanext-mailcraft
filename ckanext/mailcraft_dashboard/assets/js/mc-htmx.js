ckan.module("mc-htmx", function ($) {
    return {
        initialize: function () {
            $.proxyAll(this, /_on/);

            htmx.on("htmx:confirm", this._onHTMXconfirm);
        },

        /**
         * Handle the confirm dialog for HTMX by using SweetAlert2
         *
         * @param {Event} event The HTMX event
         */
        _onHTMXconfirm: function (event) {
            // The event is triggered on every trigger for a request, so we need to check if the element
            // that triggered the request has a confirm question set via the hx-confirm attribute,
            // if not we can return early and let the default behavior happen
            // This seems like a bug in HTMX, but it's the only way to handle the confirm dialog
            if (!event.detail.question) return

            event.preventDefault(); // Prevent the default confirm

            Swal.fire({
                title: this._('Are you sure?'),
                text: event.detail.question, // The value of `hx-confirm`
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: this._('Yes'),
                cancelButtonText: this._('Cancel'),
            }).then((result) => {
                if (result.isConfirmed) {
                    // If the user confirms, we manually issue the request
                    // true to skip the built-in window.confirm()
                    event.detail.issueRequest(true);
                }
            });
        },
    };
});
