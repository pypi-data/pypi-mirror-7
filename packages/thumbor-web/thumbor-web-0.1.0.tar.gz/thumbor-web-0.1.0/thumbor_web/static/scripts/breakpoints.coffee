class BreakpointsCtrl extends Ctrl
    gatherElements: ->
        @availableBreakpoints = [
            1,
            601,
            801,
            1281,
            1441,
            1681,
            1921
        ]
        @window = $(window)
        @breakpoints = {}

    getRandomArbitrary: (min, max) ->
        return parseInt(Math.random() * (max - min) + min, 10)

    bindEvents: ->
        @window.setBreakpoints(
            distinct: true
            breakpoints: @availableBreakpoints
        )

        for breakpoint in @availableBreakpoints
            do (breakpoint) =>
                @window.bind("enterBreakpoint#{ breakpoint }", =>
                    return unless @breakpoints[breakpoint]

                    for pair in @breakpoints[breakpoint]
                        element = pair[0]
                        image = pair[1]
                        if image instanceof Array
                            imgIndex = @getRandomArbitrary(0, image.length - 1)
                            console.log(imgIndex)
                            img = image[imgIndex]
                            element.css('background-image', "url(#{ @thumborServerUrl}/#{ img })")
                        else
                            element.css('background-image', "url(#{ @thumborServerUrl}/#{ image })")
                )

        return

    setThumborServer: (serverUrl) ->
        @thumborServerUrl = serverUrl

    addBreakpoint: (breakpoint, element, image) ->
        @breakpoints[breakpoint] = [] unless @breakpoints[breakpoint]?
        @breakpoints[breakpoint].push([element, image])
