class TestimonialsCtrl extends Ctrl
    gatherElements: ->
        @elements.username = $('#user-name')
        @elements.email = $('#user-email')
        @elements.companyName = $('#company-name')
        @elements.companyUrl = $('#company-website')
        @elements.testimonial = $('#testimonial')
        @elements.submit = @element.find('.submit a')

        @elements.new = @element.find('.new')
        @elements.success = @element.find('.success')

    bindEvents: ->
        @elements.submit.on('click', (ev) =>
            @clearValidation();
            ev.preventDefault()
            if @validate()
                data =
                    sender_name: @elements.username.val()
                    email: @elements.email.val()
                    company_name: @elements.companyName.val()
                    company_url: @elements.companyUrl.val()
                    testimonial: @elements.testimonial.val()

                $.ajax(
                    type: "POST"
                    url: '/new-testimonial'
                    data: data
                    success: @testimonialSaved
                )
        )

    testimonialSaved: =>
        @elements.new.addClass('hidden')
        @elements.success.removeClass('hidden')

    clearValidation: ->
        @elements.username.removeClass('error')
        @elements.email.removeClass('error')
        @elements.companyName.removeClass('error')
        @elements.companyUrl.removeClass('error')
        @elements.testimonial.removeClass('error')

    validate: ->
        isValid = true

        if @elements.username.val() == ''
            isValid = false
            @elements.username.addClass('error')

        if @elements.email.val() == ''
            isValid = false
            @elements.email.addClass('error')

        if @elements.companyName.val() == ''
            isValid = false
            @elements.companyName.addClass('error')

        if @elements.companyUrl.val() == ''
            isValid = false
            @elements.companyUrl.addClass('error')

        if @elements.testimonial.val() == ''
            isValid = false
            @elements.testimonial.addClass('error')

        return isValid
