
    <div>
        <form cubeaction="/cube" method="post">

            <div>If the Cube does not look right you can reload the cube or click to edit.<br></div>
            <div class="grid">

        % faceLookup = {"up":upcolors, "left":leftcolors, "front":frontcolors, "right":rightcolors, "back":backcolors, "down":downcolors}
        % for face in ["up", "left", "front", "right", "back", "down"]:
            %colors = faceLookup[face]
            % if face in ["up","left","down"]:
                <div class="row">
            % end
            % if face in ["up","down"]:
            <div class="cell" style="background-color:rgba(255, 255, 255, .4);">&nbsp;</div>
            % end
            <div class="cell">
            <div>
        <div class="grid" style="background:black">
            % for stickerIndex in range(9):
                % if stickerIndex in [0,3,6]:
                <div class="row">
                % end
                    <div class="cell" style="background:{{colors[stickerIndex]}};">
                        <div class="dropdown">
                            <button name="cube-{{name}}" class="dropbtn" style="background:{{colors[stickerIndex]}};" value="{{face}}{{stickerIndex}}=noChange" type="submit"></button>
                            <div class="dropdown-content">
                                <div class="cell">
                                % for i, color in enumerate(rubikspectrum):
                                <div style="float:right;">
                                <button class="dropbtn" style="background:{{color}};" name="cube-{{name}}"" value="{{face}}{{stickerIndex}}={{i}}" type="submit"></button>
                                </div>
                                % end
                                </div>
                            </div>
                        </div>
                    </div>
                % if stickerIndex in [2,5,8]:
                </div>
                % end

            % end
            </div>
        </div>
    </div>

    % if face in ["up","down"]:
    <div class="cell" style="background-color:rgba(255, 255, 255, .4);">&nbsp;</div>
    <div class="cell" style="background-color:rgba(255, 255, 255, .4);">&nbsp;</div>
    % end
        % if face in ["up","back","down"]:
    </div>
        % end
        % end
</div>
        </form> 
    </div>
