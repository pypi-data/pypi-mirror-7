class HeaderCtrl extends Ctrl
    gatherElements: ->
        @elements =
            menu: @element.find('nav')
            main: @element.find('.main')
            learn: @element.find('.learn-more')

        @top = 120
        @bottom = @elements.main.offset().top
        @opaqueMin = @element.height() - @elements.menu.height()

    bindEvents: ->
        $(document).scrollspy
            onTick: (element, position, inside, enters, leaves) =>
                if position.top < @top
                    @elements.main.css('opacity', 100)
                    @elements.learn.css('opacity', 100)
                    return

                opacity = (@bottom - position.top) / (@bottom - @top)
                @elements.main.css('opacity', opacity)
                @elements.learn.css('opacity', opacity)

        @elements.menu.scrollspy
            min: 15
            max: 10000000000
            onEnter: (element, position) =>
                @elements.menu.addClass('static')
            onLeave: (element, position) =>
                @elements.menu.removeClass('static')
        .scrollspy
            min: @opaqueMin
            max: 10000000000
            onEnter: (element, position) =>
                @elements.menu.addClass('opaque')
            onLeave: (element, position) =>
                @elements.menu.removeClass('opaque')
